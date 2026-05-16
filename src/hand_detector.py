import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

HAND_CONNECTIONS = [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),
    (0, 5),
    (5, 6),
    (6, 7),
    (7, 8),
    (0, 9),
    (9, 10),
    (10, 11),
    (11, 12),
    (0, 13),
    (13, 14),
    (14, 15),
    (15, 16),
    (0, 17),
    (17, 18),
    (18, 19),
    (19, 20),
    (5, 9),
    (9, 13),
    (13, 17),
]


def draw_hand(frame, landmarks, connections):
    h, w = frame.shape[:2]
    for landmark in landmarks:
        x = int(landmark.x * w)
        y = int(landmark.y * h)
        cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

    for start, end in connections:
        start_pt = (int(landmarks[start].x * w), int(landmarks[start].y * h))
        end_pt = (int(landmarks[end].x * w), int(landmarks[end].y * h))
        cv2.line(frame, start_pt, end_pt, (0, 255, 0), 2)


def main():
    cap = cv2.VideoCapture(0)

    base_options = python.BaseOptions(model_asset_path="hand_landmarker.task")
    options = vision.HandLandmarkerOptions(
        base_options=base_options, num_hands=1, running_mode=vision.RunningMode.VIDEO
    )

    with vision.HandLandmarker.create_from_options(options) as detector:
        frame_idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

            result = detector.detect_for_video(mp_image, frame_idx)
            frame_idx += 1

            if result.hand_landmarks:
                for hand_landmarks in result.hand_landmarks:
                    draw_hand(frame, hand_landmarks, HAND_CONNECTIONS)

            cv2.imshow("Hand Detection", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
