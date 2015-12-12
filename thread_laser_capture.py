import threading
import cv2.cv as cv
import cv2
import sys
import np
from time import sleep

CAMERA_TO_CHOOSE = 1  # device number. 0 for laptop is usually the frontCam, so for webCam use 1
SLEEP_TIME_BETWEEN_FRAMES_MS = 5
SLEEP_TIME_BETWEEN_STAGES_SEC = 5

STAGE_0_DISPLAY_MOVEMENT_AND_CATCH_CORNERS, STAGE_1_WORK_IN_BACKGROUND = 0, 1


class ThreadLaserCapture(threading.Thread):
    def __init__(self, manager, cam_width=640, cam_height=480, hue_min=20, hue_max=160,
                 sat_min=100, sat_max=255, val_min=200, val_max=256,
                 display_thresholds=False):
        """
        * ``cam_width`` x ``cam_height`` -- This should be the size of the
        image coming from the camera. Default is 640x480.

        HSV color space Threshold values for a RED laser pointer are determined
        by:

        * ``hue_min``, ``hue_max`` -- Min/Max allowed Hue values
        * ``sat_min``, ``sat_max`` -- Min/Max allowed Saturation values
        * ``val_min``, ``val_max`` -- Min/Max allowed pixel values

        If the dot from the laser pointer doesn't fall within these values, it
        will be ignored.

        * ``display_thresholds`` -- if True, additional windows will display
          values for threshold image channels.

        """

        super(ThreadLaserCapture, self).__init__()
        self.daemon = True

        self.laser_place = None  # will be re-captured at the start of turning the camera on
        self.manager = manager
        self.exit = False
        self.stage = STAGE_0_DISPLAY_MOVEMENT_AND_CATCH_CORNERS

        self.corners = [None, None, None, None]
        self.ave_x = self.ave_y = None   # temp registers for the corner capture

        self.cam_width = cam_width
        self.cam_height = cam_height
        self.hue_min = hue_min
        self.hue_max = hue_max
        self.sat_min = sat_min
        self.sat_max = sat_max
        self.val_min = val_min
        self.val_max = val_max
        self.capture = None  # camera capture device
        self.channels = {
            'hue': None,
            'saturation': None,
            'value': None,
            'laser': None,
        }

    def setup_windows(self):
        sys.stdout.write("Using OpenCV version: {0}\n".format(cv2.__version__))

        # create output windows
        self.create_and_position_window('LaserPointer', 0, 0)
        # self.create_fullscreen_window('LaserPointer')  # TODO SHOW will be usefull
        self.create_and_position_window('RGB_VideoFrame',
            10 + self.cam_width, 0)

    def create_and_position_window(self, name, xpos, ypos):
        """Creates a named widow placing it on the screen at (xpos, ypos)."""
        # Create a window
        cv2.namedWindow(name, cv2.CV_WINDOW_AUTOSIZE)
        # Resize it to the size of the camera image
        cv2.resizeWindow(name, self.cam_width, self.cam_height)
        # Move to (xpos,ypos) on the screen
        cv2.moveWindow(name, xpos, ypos)

    def setup_camera_capture(self, device_num=CAMERA_TO_CHOOSE):
        """
        Perform camera setup for the device number (default device = 0).
        Returns a reference to the camera Capture object.

        """
        try:
            device = int(device_num)
            sys.stdout.write("Using Camera Device: {0}\n".format(device))
        except (IndexError, ValueError):
            # assume we want the 1st device
            device = 0
            sys.stderr.write("Invalid Device. Using default device 0\n")

        # Try to start capturing frames
        self.capture = cv2.VideoCapture(device)
        if not self.capture.isOpened():
            sys.stderr.write("Faled to Open Capture device. thread quitting.\n")
            self.manager.laser_daemon_encountered_exit = True
            sys.exit(1)

        # set the wanted image size from the camera
        self.capture.set(
            cv.CV_CAP_PROP_FRAME_WIDTH,
            self.cam_width
        )
        self.capture.set(
            cv.CV_CAP_PROP_FRAME_HEIGHT,
            self.cam_height
        )
        return self.capture

    def threshold_image(self, channel):
        if channel == "hue":
            minimum = self.hue_min
            maximum = self.hue_max
        elif channel == "saturation":
            minimum = self.sat_min
            maximum = self.sat_max
        elif channel == "value":
            minimum = self.val_min
            maximum = self.val_max
        else:   # will never happen
            minimum = maximum = None

        (t, tmp) = cv2.threshold(
            self.channels[channel],  # src
            maximum,  # threshold value
            0,  # we dont care because of the selected type
            cv2.THRESH_TOZERO_INV #t type
        )

        (t, self.channels[channel]) = cv2.threshold(
            tmp,  # src
            minimum,  # threshold value
            255,  # maxvalue
            cv2.THRESH_BINARY # type
        )

        if channel == 'hue':
            # only works for filtering red color because the range for the hue is split
            self.channels['hue'] = cv2.bitwise_not(self.channels['hue'])

    def detect(self, frame):
        hsv_img = cv2.cvtColor(frame, cv.CV_BGR2HSV)

        # split the video frame into color channels
        h, s, v = cv2.split(hsv_img)
        self.channels['hue'] = h
        self.channels['saturation'] = s
        self.channels['value'] = v

        # Threshold ranges of HSV components; storing the results in place
        self.threshold_image("hue")
        self.threshold_image("saturation")
        self.threshold_image("value")

        # Perform an AND on HSV components to identify the laser!
        self.channels['laser'] = cv2.bitwise_and(
            self.channels['hue'],
            self.channels['value']
        )
        self.channels['laser'] = cv2.bitwise_and(  # use !saturation as it gets best results
            cv2.bitwise_not(self.channels['saturation']),
            self.channels['laser']
        )

        if self.stage == STAGE_0_DISPLAY_MOVEMENT_AND_CATCH_CORNERS:
            # Merge the HSV components back together.
            hsv_image = cv2.merge([
                self.channels['laser'],
                self.channels['laser'],
                self.channels['laser'],
            ])
            return hsv_image
        return None

    def work_on_detected(self):
        cpy = np.copy(self.channels['laser'])
        height, width = cpy.shape

        indices = np.transpose(np.where(cpy > 0))
        if indices.any():
            sum_y, sum_x = np.sum(indices, axis=0)
            self.ave_y, self.ave_x = sum_y/len(indices), sum_x/len(indices)

            # print("average x:", self.ave_x, "average y:", self.ave_y)
            self.manager.update_player_place((self.ave_x, self.ave_y))

    def display(self, img, frame):
        """Display the combined image and (optionally) all other image channels
        NOTE: default color space in OpenCV is BGR.
        """
        cv2.imshow('RGB_VideoFrame', frame)
        cv2.imshow('LaserPointer', self.channels['laser'])

        key = cv2.waitKey(SLEEP_TIME_BETWEEN_FRAMES_MS)
        if key == ord('1'):
            self.corners[0] = self.ave_x, self.ave_y
        elif key == ord('2'):
            self.corners[1] = self.ave_x, self.ave_y
        elif key == ord('3'):
            self.corners[2] = self.ave_x, self.ave_y
        elif key == ord('4'):
            self.corners[3] = self.ave_x, self.ave_y
        elif key == ord('q'):
            cv2.destroyAllWindows()
            print("As the user requested, Laser-capture thread quitting.")
            self.manager.laser_daemon_encountered_exit = True
            exit()

    def all_corners_are_ready(self):
        ready = True
        for corner in self.corners:
            if not corner:
                ready = False
        return ready

    def run(self):
        # Set up window positions
        self.setup_windows()
        # Set up the camera capture
        self.setup_camera_capture()
        while not self.exit:
            # 1. capture the current image
            success, frame = self.capture.read()
            if not success: # no image captured... end the processing
                sys.stderr.write("Could not read camera frame. thread Quitting.\n")
                self.manager.laser_daemon_encountered_exit = True
                sys.exit(1)

            hsv_image = self.detect(frame)
            self.work_on_detected()

            if self.stage == STAGE_0_DISPLAY_MOVEMENT_AND_CATCH_CORNERS:
                self.display(hsv_image, frame)
                if self.all_corners_are_ready():
                    cv2.destroyAllWindows()
                    self.manager.init_calculator(*self.corners)
                    sleep(SLEEP_TIME_BETWEEN_STAGES_SEC)
                    self.stage = STAGE_1_WORK_IN_BACKGROUND

            elif self.stage == STAGE_1_WORK_IN_BACKGROUND:
                sleep(ms_to_sec(SLEEP_TIME_BETWEEN_FRAMES_MS))
        print("laser capture daemon dies now")

    def exit_async(self):
        self.exit = True

def ms_to_sec(ms):
    return 0.001 * ms
