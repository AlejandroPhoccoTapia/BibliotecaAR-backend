from io import BytesIO

from PIL import Image, ImageOps


class FaceRecognitionError(ValueError):
    pass


SIGNATURE_SIZE = 128
CELL_SIZE = 32
LBP_BINS = 16


def build_face_signature(file_obj):
    image = _open_image(file_obj)
    face = _crop_face(image)
    normalized = ImageOps.equalize(face.convert('L').resize((SIGNATURE_SIZE, SIGNATURE_SIZE)))
    return _lbp_histogram(normalized)


def compare_signatures(first, second):
    if not first or not second or len(first) != len(second):
        raise FaceRecognitionError('Las firmas faciales no son comparables.')

    distance = 0
    for left, right in zip(first, second):
        denominator = left + right
        if denominator:
            distance += ((left - right) ** 2) / denominator

    return distance * 0.5


def _open_image(file_obj):
    try:
        position = file_obj.tell()
    except (AttributeError, OSError):
        position = None

    raw = file_obj.read()

    if position is not None:
        file_obj.seek(position)
    elif hasattr(file_obj, 'seek'):
        file_obj.seek(0)

    try:
        return Image.open(BytesIO(raw)).convert('RGB')
    except Exception as exc:
        raise FaceRecognitionError('No se pudo leer la imagen facial.') from exc


def _crop_face(image):
    detected = _crop_with_opencv(image)
    if detected:
        return detected

    width, height = image.size
    side = min(width, height)
    left = (width - side) // 2
    top = (height - side) // 2
    return image.crop((left, top, left + side, top + side))


def _crop_with_opencv(image):
    try:
        import cv2
        import numpy as np
    except ImportError:
        return None

    array = np.array(image)
    gray = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY)
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    classifier = cv2.CascadeClassifier(cascade_path)
    faces = classifier.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(48, 48))

    if len(faces) == 0:
        return None

    x, y, width, height = max(faces, key=lambda face: face[2] * face[3])
    margin = int(max(width, height) * 0.18)
    left = max(x - margin, 0)
    top = max(y - margin, 0)
    right = min(x + width + margin, image.width)
    bottom = min(y + height + margin, image.height)
    return image.crop((left, top, right, bottom))


def _lbp_histogram(image):
    pixels = image.load()
    cells_per_side = SIGNATURE_SIZE // CELL_SIZE
    histogram = [0] * (cells_per_side * cells_per_side * LBP_BINS)

    for y in range(1, SIGNATURE_SIZE - 1):
        for x in range(1, SIGNATURE_SIZE - 1):
            center = pixels[x, y]
            code = 0
            code |= (pixels[x - 1, y - 1] >= center) << 7
            code |= (pixels[x, y - 1] >= center) << 6
            code |= (pixels[x + 1, y - 1] >= center) << 5
            code |= (pixels[x + 1, y] >= center) << 4
            code |= (pixels[x + 1, y + 1] >= center) << 3
            code |= (pixels[x, y + 1] >= center) << 2
            code |= (pixels[x - 1, y + 1] >= center) << 1
            code |= pixels[x - 1, y] >= center

            cell_x = min(x // CELL_SIZE, cells_per_side - 1)
            cell_y = min(y // CELL_SIZE, cells_per_side - 1)
            cell_index = cell_y * cells_per_side + cell_x
            bin_index = code // (256 // LBP_BINS)
            histogram[cell_index * LBP_BINS + bin_index] += 1

    total = sum(histogram)
    if not total:
        raise FaceRecognitionError('No se pudo generar una firma facial valida.')

    return [round(value / total, 8) for value in histogram]
