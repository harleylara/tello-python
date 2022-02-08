import cv2

LOCAL_IP = '0.0.0.0'
VIDEO_STREAMING_PORT = 11111

INPUT_STR = f'udp://@{LOCAL_IP}:{VIDEO_STREAMING_PORT}'
cap = cv2.VideoCapture(INPUT_STR, cv2.CAP_FFMPEG)

while True:
    re, image = cap.read()
    if not re:
        pass
    else:
        cv2.imshow('frame', image)
        cv2.waitKey(1)
