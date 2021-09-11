from PIL import Image
from collections import deque
import numpy as np
import warnings


class ImageThresholdUtil:
    """
    It has to do with the image threshold. Threshold here means filtering,
    which finds the pixels to be filtered out. So this class has static methods
    related to the threshold and cooperates in context.
    """

    @staticmethod
    def get_threshold_pixels(row, col, image, rep_count, target_rate) -> list:
        """
        It does the job of finding a threshold in the image.
        It has an algorithm that reads an image and calculates
        which pixels are used the most and what their proportions are.

        :param row: int
            image's row size
        :param col: int
            image's column size
        :param image: ndarray
            image loaded by Pillow Image module and change to numpy array
        :param rep_count: int
            Indicates the number of candidates. The candidate group is a group of pixels
            that can become threshold points, and is an argument for
            how much this candidate group will be accommodated.
        :param target_rate: int
            Check how many pixels in the image are being used.
            Then divide this number of used pixels by total image and multiply by
            100 to calculate the percentage. In other words, the ratio of pixels
            is calculated, and it is a setting argument for which ratio to set as a valid value.

        :return: ndarray
            Output array which has threshold points
        """
        area = row * col
        rep_count = rep_count * -1
        _, counts = np.unique(image, return_counts=True)
        parted_ind = np.argpartition(counts, rep_count)[rep_count:]
        ratio_counts = counts[parted_ind] / area * 100
        threshold_pixels = (ratio_counts > target_rate).nonzero()[0]
        if threshold_pixels is None:
            return []
        return parted_ind[threshold_pixels]


class RectangleImageCrop:
    """
    This class was created to crop an image into a rectangle.
    After opening the image, it automatically detects the background, then detects the effective area and crops it.
    Background detection works based on rules. Right now it's based on how many coherent pixels are found.
    Then, the image is converted to a NumPy array rather than a list,
    and the average of the RGB values is calculated and the pixels are merged into one.
    """

    __pix, __img = None, None
    __row, __col = None, None
    __img_field = None, None
    __min_width, __min_height = None, None
    __direction_row = [0, 1, 0, -1]
    __direction_col = [1, 0, -1, 0]
    __pixel_sensitivity = 5
    __occupancy_rate = 10
    __candidate_threshold_group = 3
    __threshold_pixels = None
    __save_points = []

    def open(self, image_path, auto_threshold_detection=True) -> None:
        """
        The image will open. The way to open it is using the PIL library.
        And this image will be converted to RGB option.

        :param image_path:
            The path where the image file exists.
        :param auto_threshold_detection:
            Option to automatically detect thresholds. When the value of this option is True,
            the threshold is selected based on the rules. In case of False, the function has not been added yet.
            I plan to add an option to let users enter their own thresholds.
        :return: None
            There is no return value. It is assigned to a class internal variable.
        """
        self.__img = Image.open(image_path).convert('RGB')
        self.__row, self.__col = self.__img.size
        self.__numpy_mean_variant()

    def __numpy_mean_variant(self) -> None:
        """
        Reads an image file and converts it to a NumPy array. During the conversion process,
        only one value is extracted as the average value of the RGB channels.

        :return: None
            There is no return value. It is assigned to a class internal variable.
        """
        self.__img_field = np.zeros((self.__col, self.__row))
        average_pixel_values = np.mean(np.array(self.__img), axis=2, keepdims=True)
        self.__pix = np.rint(np.concatenate([average_pixel_values], axis=2))

    def __validate_image_size(self, upper_left_point, bottom_right_point) -> bool:
        """
        It reads the width and height of the extracted image and verifies
        whether the image meets the conditions.

        :return: bool
            It returns True or False according to the verification result.
        """
        x1, y1 = upper_left_point
        x2, y2 = bottom_right_point
        height = y2 - y1
        width = x2 - x1
        return width > self.__min_width and height > self.__min_height

    def __validate_image_pixel(self, row, col):
        """
        Algorithm for traversing image pixels. It checks the validity of image pixels by mixing
        an algorithm called breadth-first search and a rule-based algorithm.

        :param row: int
            image's row size
        :param col: int
            image's column size
        :return: list, bool
            Returns a list containing the coordinate values of the image, or False.
        """
        self.__img_field[row][col] = 1
        temp_upper_bottom_points = []
        point = [row, col]
        q = deque()
        q.append((row, col))
        temp_upper_bottom_points.append(point)
        while q:
            row_x, row_y = q.popleft()
            point = [row_x, row_y]
            for i in range(4):
                mx = row_x + self.__direction_row[i]
                my = row_y + self.__direction_col[i]
                if 0 <= mx < self.__col and 0 <= my < self.__row:
                    if self.__img_field[mx][my] == 0 and self.__validate_pixel(mx, my):
                        self.__img_field[mx][my] = 1
                        q.append((mx, my))
        temp_upper_bottom_points.append(point)
        if self.__validate_image_size(temp_upper_bottom_points[0], temp_upper_bottom_points[1]):
            return temp_upper_bottom_points
        else:
            return False

    def __validate_pixel(self, row, col) -> bool:
        """
        Check the validity of the pixel values along with the threshold.
        Pixel sensitivity relates to how much blurring can be achieved at
        a threshold point, and acts as a masking agent.

        :param row: int
            image's row size
        :param col: int
            image's column size
        :return: bool
            Returns the validation value as a bool type.
        """
        for pixel in self.__threshold_pixels:
            if pixel - self.__pixel_sensitivity <= self.__pix[row, col] <= pixel + self.__pixel_sensitivity:
                return False
        return True

    def __iterate_pixel(self) -> None:
        """
        A double loop for traversing the pixels. A check is being made on the pixels that have been traversed.

        :return: None
            Save the upper and lower pixel positions of the image in the member variable save_points.
            It doesn't return any value. Save the upper and lower pixel positions of the image
            If you want to save the image based on the extracted crop points values, call the 'save' method.
            If you want to receive only the crop points value, call 'get_crop_points'.
        """
        for j in range(self.__row):
            for i in range(self.__col):
                if self.__img_field[i][j] == 0 and self.__validate_pixel(i, j) is True:
                    result = self.__validate_image_pixel(i, j)
                    if result:
                        self.__save_points.append(result)

    def crop(self, min_crop_width=100, min_crop_height=100, occupancy_rate=10, candidate_threshold_group=3, pixel_sensitivity=10):
        """
        This method cuts the image into a rectangular shape. A separate function call is required to save the image

        :param min_crop_width: int
            The minimum width of the image you want to crop. Values below this are ignored.
        :param min_crop_height: int
            The minimum height of the image you want to crop. Values below this are ignored.
        :param occupancy_rate: int
            When choosing a threshold, it is affected by the frequency of pixels across the image.
            It indicates how much of a single or multiple background pixels that are not
            in the image to be cropped out of the overall image. For example, if the percentage of white background
            in the entire image is more than 10%, this number can be regarded as 10.
        :param candidate_threshold_group: int
            It is an option to decide how many threshold candidates to extract when calculating
            the threshold along with the above occupancy_rate.
            For example, if this value is 5, up to 5 threshold pixels are extracted.
        :param pixel_sensitivity: int
            While traversing the pixels, the verification process for the threshold is included,
            and it is an option for how much blur to apply this threshold.
        :exception TypeError: If the arguments are not int.
        :exception ValueError: If the arguments are not positive, or If the argument values are too large or too small
        :exception RuntimeError: If threshold points are emtpy.
        :return: None
            Save the upper and lower pixel positions of the image in the member variable save_points.
        """

        if not isinstance(min_crop_width, int):
            raise TypeError("min_width must be a int")
        if min_crop_width <= 0:
            raise ValueError("min_width must be a positive. bigger than 0")

        if not isinstance(min_crop_height, int):
            raise TypeError("min_width must be a int")
        if min_crop_height <= 0:
            raise ValueError("min_width must be a positive. bigger than 0")

        if not isinstance(occupancy_rate, int):
            raise TypeError("occupancy_rate must be a int")
        if occupancy_rate <= 0:
            raise ValueError("occupancy_rate must be a positive. bigger than 0")

        if not isinstance(candidate_threshold_group, int):
            raise TypeError("candidate_threshold_group must be a int")
        if candidate_threshold_group <= 0:
            raise ValueError("candidate_threshold_group must be a positive. bigger than 0")

        if not isinstance(pixel_sensitivity, int):
            raise TypeError("candidate_threshold_group must be a int")
        if pixel_sensitivity <= 0:
            raise ValueError("pixel_sensitivity must be a positive. bigger than 0")

        if self.__occupancy_rate < 7:
            warnings.warn(
                "occupancy_rate is too low. Performance degradation is possible. "
                "It is recommended to have a value of 10 or more.",)
        if self.__candidate_threshold_group > 5:
            warnings.warn(
                "candidate_threshold_group is too large. Performance degradation is possible. "
                "It is recommended to have a value of 5 or smaller.",
            )

        if self.__pixel_sensitivity > 10:
            warnings.warn(
                "pixel_sensitivity is too large. Performance degradation is possible. "
                "effective range too large. The drop in accuracy can be large. "
                "It is recommended to have a value of between 5 and 10")

        if self.__pixel_sensitivity < 5:
            warnings.warn(
                "pixel_sensitivity is too small. Performance degradation is possible. "
                "effective range too large. The drop in accuracy can be large. "
                "It is recommended to have a value of between 5 and 10")

        self.__min_width = min_crop_height
        self.__min_height = min_crop_width
        self.__occupancy_rate = occupancy_rate
        self.__candidate_threshold_group = candidate_threshold_group
        self.__pixel_sensitivity = pixel_sensitivity
        self.__threshold_pixels = ImageThresholdUtil.get_threshold_pixels(self.__row, self.__col, self.__pix, self.__candidate_threshold_group, self.__occupancy_rate)
        if not self.__threshold_pixels:
            raise RuntimeError("threshold pixels are empty. No threshold pixels were detected. "
                               "drop a occupancy_rate value")
        self.__iterate_pixel()

    def save(self, saved_path, filename, saved_format) -> None:
        """
        This method saves the image. Since there can be many images,
        they are saved with an incrementing number after the file name.
        For example, crop_1.jpeg, crop_2.jpeg

        :param saved_path: str
            This is the path to the file you want to save.
        :param filename: str
            File name to save
        :param saved_format: format
            File format to save
        :return: None
        """
        for idx, point in enumerate(self.__save_points):
            box = (point[0][1], point[0][0], point[1][1], point[1][0])
            crop_img = self.__img.crop(box)
            saved_filename = filename + '_' + str(idx + 1) + '.' + saved_format.lower()
            crop_img.save(saved_path + '/' + saved_filename, format=saved_format)

    def get_threshold_pixels(self) -> list:
        """
        Get the extracted threshold.

        :exception RuntimeError: If threshold points are emtpy.
        :return: list
            extracted threshold points
        """
        if self.__threshold_pixels is None:
            raise RuntimeError("threshold pixels are None. crop method must be done before this method.")
        return self.__threshold_pixels

    def get_crop_points(self) -> list:
        """
        Get the crop points

        :return: list
            extracted crop points
        """
        points = []
        for point in self.__save_points:
            points.append((point[0][1], point[0][0], point[1][1], point[1][0]))
        return points