import cv2
import mediapipe as mp


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

stop_sign = False


class shoulder:
    def __init__(self, left_shoulder, right_shoulder):
        self.left_shoulder = left_shoulder
        self.right_shoulder = right_shoulder

class hand:
    def __init__(self, elbow, wrist, pinky, index, thumb):
        self.elbow = elbow
        self.wrist = wrist
        self.pinky = pinky
        self.index = index
        self.thumb = thumb

def compare(shoulder, left_hand, right_hand):
    left_hand = left_hand.__dict__.values()
    right_hand = right_hand.__dict__.values()
    left_sign = all(y < shoulder.left_shoulder for y in left_hand)
    right_sign = all(y < shoulder.right_shoulder for y in right_hand)
    return left_sign or right_sign

def handle_sign():
    global stop_sign
    cap = cv2.VideoCapture(0)
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                # If loading a video, use 'break' instead of 'continue'.
                continue

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = pose.process(image)

            try:
                # get post
                left_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].y
                right_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].y
                
                shoulder_info =    shoulder(left_shoulder=left_shoulder, right_shoulder=right_shoulder)

                left_elbow = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW].y
                left_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST].y
                left_pinky = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_PINKY].y
                left_index = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_INDEX].y
                left_thumb = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_THUMB].y
                left_hand_info = hand(elbow=left_elbow, wrist=left_wrist, pinky=left_pinky, index=left_index, thumb=left_thumb)


                right_elbow = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW].y
                right_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].y
                right_pinky = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_PINKY].y
                right_index = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_INDEX].y
                right_thumb = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_THUMB].y
                right_hand_info = hand(elbow=right_elbow, wrist=right_wrist, pinky=right_pinky, index=right_index, thumb=right_thumb)


                status = compare(shoulder_info, left_hand_info, right_hand_info)
                yield status
            except:
                pass


            # Draw the pose annotation on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
            # Flip the image horizontally for a selfie-view display.
            cv2.imshow('MediaPipe Pose', cv2.flip(image, 1))
            if cv2.waitKey(1) & 0xFF == ord('q') or stop_sign:
                    break
    cap.release()

    cv2.destroyAllWindows()

if __name__=="__main__":
    for i in handle_sign():
        print(i)


