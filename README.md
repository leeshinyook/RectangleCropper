# RectangleCropper


[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fleeshinyook%2FRectangleCropper&count_bg=%23F3007A&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)
![Generic badge](https://img.shields.io/badge/version-1.0.0-green.svg)

## Overview

`RectangleCropper` is a Python library that crops images into rectangles. The image to be cropped is detected through the rule base with pixel search algorithm.
For example, the image below shows a bestseller in a bookstore, and you want to crop the image of the book. 
RectangleCropper automatically detects the object area and crop it!
Just pass the image to the RectangleCropper and it will be cropped like magic.

#### 1. BookStore
<img width="600" alt="스크린샷 2021-09-11 오후 10 12 09" src="https://user-images.githubusercontent.com/55838461/132948980-b6a3f9f4-57b7-4b42-bf38-86d6a287a2b5.png">

#### 2. OpenMarket
<img width="600" alt="스크린샷 2021-09-11 오후 10 13 07" src="https://user-images.githubusercontent.com/55838461/132949225-345d9962-65c7-422b-81cb-331791ef64ac.png">

#### 3. NewPaper
<img width="600" alt="스크린샷 2021-09-11 오후 10 13 33" src="https://user-images.githubusercontent.com/55838461/132949267-cb03e2a2-8923-4569-841f-517faa1992b2.png">

#### 4. WebSite
<img width="600" alt="스크린샷 2021-09-11 오후 10 15 34" src="https://user-images.githubusercontent.com/55838461/132949306-b966a0a3-9c26-4b5c-87e2-41da3b735ee4.png">

#### 5. Google Image 
<img width="600" alt="스크린샷 2021-09-11 오후 10 29 15" src="https://user-images.githubusercontent.com/55838461/132949483-b1fb9845-e08a-4b9a-85eb-71cdc9cebdde.png">


There are many services that use square-based images. There are many services that use square-based images. This library was created by combining a general rule-based algorithm and a pixel-based search algorithm, not advanced technologies such as computer vision.
So it doesn't have enough ability to cover the edge case. This library shows the best performance when the background color is one color or two or three. So it doesn't have enough ability to cover the edge case. However, by applying this rule-based algorithm, it became possible to apply rules according to the service. For example, you can input guidelines for the size of the image to be cropped, and finely adjust the critical point required when cropping the image.


## Requirements

- Python >= 3
- Works on Linux, Windows, macOS

## Getting it

The quick way:
```code
pip install RectangleCropper
```

## Getting Started

```python
import rectanglecropper.crop as rc

cropper = rc.RectangleImageCrop()
cropper.open(image_path='images/image1.png')
cropper.crop()
cropper.save(saved_path='cropimages', filename='image1', saved_format='jpeg')
```
Done!

## Performance

Unless you need a lot of image processing, I recommend using this library. 
However, performance cannot be guaranteed. Because this library is going through the pixel-based search process. 
In Python, the cost of this process is very high. It works by converting to NumPy inside, not a list, but it doesn't change the fact that it's expensive. 
If you process many images at once, the memory may not be able to support it or it will take a very long time. 
Also, the larger the image size, the longer the cropping process takes. To solve the above cost problem, 
I will make a library of the same function written in Golang which is at least 5-7 times faster and will distribute it soon. thank you.

## Advanced Usage

Is the image not cropping well? 

Then I recommend adjusting the options of the crop method.

- min_crop 
```python
import rectanglecropper.crop as rc

cropper = rc.RectangleImageCrop()
cropper.open(image_path='images/image1.png')
cropper.crop(min_crop_width=1000, min_crop_height=1000)
cropper.save(saved_path='cropimages', filename='image1', saved_format='jpeg')
```

The min_crop option above specifies the minimum size when cropping an image. 
If the option is 1000, it is ignored if the cropped size is less than 1000.

- occupancy_rate
```python
import rectanglecropper.crop as rc

cropper = rc.RectangleImageCrop()
cropper.open(image_path='images/image1.png')
cropper.crop(occupancy_rate=30)
cropper.save(saved_path='cropimages', filename='image1', saved_format='jpeg')
```
<img width="600" alt="스크린샷 2021-09-11 오후 11 01 30" src="https://user-images.githubusercontent.com/55838461/132950475-bcf46042-4df6-4bb2-9a32-6f70e559d8c1.png">


Probably, the background in this photo is black, and the images to be cropped are blue and yellow boxes. If you want to crop only the blue box here, you can enter the above option greater than 18. That is, the occupancy_rate can be filtered by determining the ratio based on the RGB channel.

- pixel_sensitivity
```python
import rectanglecropper.crop as rc

cropper = rc.RectangleImageCrop()
cropper.open(image_path='images/image1.png')
cropper.crop(pixel_sensitivity=5)
cropper.save(saved_path='cropimages', filename='image1', saved_format='jpeg')
```
<img width="600" alt="스크린샷 2021-09-11 오후 11 10 30" src="https://user-images.githubusercontent.com/55838461/132950695-bddd0e43-7a16-4197-9aa9-9374b6698073.png">

The image is composed of RGB channels, so if you look closely, continuous channels are connected. 
If pixel sensitivity is given, the adjacent pixels are masked to see the same value. If the pixel values between the images to be cropped are not the same and are blurry, 
it is recommended to try the above option.

- candidate_threshold_group
```python
import rectanglecropper.crop as rc

cropper = rc.RectangleImageCrop()
cropper.open(image_path='images/image1.png')
cropper.crop(candidate_threshold_group=5)
cropper.save(saved_path='cropimages', filename='image1', saved_format='jpeg')
```
An image that is approached in units of pixels divides the area according to a threshold value.
If there are various RGB channels in the area to be divided, it is recommended to adjust the above options.



In fact, it is necessary to understand the option values related to this crop. 
So, I set the initial value in advance, and if you need to customize it, 
please set it not to deviate too much from this default value.

## Finally

Many features will be added in the future. 

If you have any problems, I'd appreciate it if you could leave them in the issue.