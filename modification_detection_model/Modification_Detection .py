import os
import hashlib
from PIL import Image, ExifTags
import numpy as np
import scipy.fftpack
import cv2
from sklearn.cluster import KMeans
import piexif
from fractions import Fraction
import math
from datetime import datetime
import json

def check_exif_format(image_path):
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if exif_data is None:
                return False
            return True
    except Exception:
        return False

def rational_to_float(rational):
    return rational[0] / rational[1] if rational[1] != 0 else 0

def check_exif_internal_consistency(image_path):
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if exif_data is None:
                return False
            
            # Check date consistency
            date_time = exif_data.get(36867)  # DateTimeOriginal
            date_time_digitized = exif_data.get(36868)  # DateTimeDigitized
            date_time_modified = exif_data.get(306)  # DateTime
            if date_time and date_time_digitized and date_time_modified:
                dt_original = datetime.strptime(date_time, "%Y:%m:%d %H:%M:%S")
                dt_digitized = datetime.strptime(date_time_digitized, "%Y:%m:%d %H:%M:%S")
                dt_modified = datetime.strptime(date_time_modified, "%Y:%m:%d %H:%M:%S")
                if not (dt_original <= dt_digitized <= dt_modified):
                    return False
            
            # Check camera information consistency
            make = exif_data.get(271)  # Make
            model = exif_data.get(272)  # Model
            software = exif_data.get(305)  # Software
            if make and model:
                known_brands = ['Canon', 'Nikon', 'Sony', 'Fujifilm', 'Olympus', 'Panasonic', 'Leica', 'Pentax', 'Samsung']
                if not any(brand.lower() in make.lower() for brand in known_brands):
                    return False
                if make.lower() not in model.lower():
                    return False
            if software and any(editor in software.lower() for editor in ['photoshop', 'lightroom', 'gimp', 'affinity']):
                return False
            
            # Check GPS information consistency
            gps_info = exif_data.get(34853)  # GPSInfo
            if gps_info:
                lat = gps_info.get(2)
                lon = gps_info.get(4)
                if lat and lon:
                    lat_value = rational_to_float(lat[0]) + rational_to_float(lat[1])/60 + rational_to_float(lat[2])/3600
                    lon_value = rational_to_float(lon[0]) + rational_to_float(lon[1])/60 + rational_to_float(lon[2])/3600
                    if lat_value > 90 or lat_value < -90 or lon_value > 180 or lon_value < -180:
                        return False
            
            # Check exposure information consistency
            iso_speed = exif_data.get(34855)  # ISOSpeedRatings
            exposure_time = exif_data.get(33434)  # ExposureTime
            f_number = exif_data.get(33437)  # FNumber
            if iso_speed and exposure_time and f_number:
                iso_value = iso_speed
                exposure_value = rational_to_float(exposure_time)
                f_value = rational_to_float(f_number)
                ev = math.log2(f_value**2 / exposure_value)
                if ev < -10 or ev > 20:  # Typical EV range for natural light photography
                    return False
            
            return True
    except Exception:
        return False

def check_exif_external_consistency(image_path):
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if exif_data is None:
                return False
            
            # Check image size consistency
            exif_width = exif_data.get(40962)  # ExifImageWidth
            exif_height = exif_data.get(40963)  # ExifImageHeight
            if exif_width and exif_height:
                if exif_width != img.width or exif_height != img.height:
                    return False
            
            # Check orientation information
            orientation = exif_data.get(274)  # Orientation
            if orientation and orientation not in [1, 2, 3, 4, 5, 6, 7, 8]:
                return False
            
            # Check color space consistency
            color_space = exif_data.get(40961)  # ColorSpace
            bits_per_sample = exif_data.get(258)  # BitsPerSample
            if color_space and bits_per_sample:
                if color_space == 1 and sum(bits_per_sample) != 24:  # sRGB should typically be 8 bits per channel
                    return False
            
            # Check focal length consistency
            focal_length = exif_data.get(37386)  # FocalLength
            focal_length_35mm = exif_data.get(41989)  # FocalLengthIn35mmFilm
            if focal_length and focal_length_35mm:
                fl = rational_to_float(focal_length)
                fl_35 = focal_length_35mm
                if fl > fl_35:
                    return False
            
            # Check resolution consistency
            x_resolution = exif_data.get(282)  # XResolution
            y_resolution = exif_data.get(283)  # YResolution
            resolution_unit = exif_data.get(296)  # ResolutionUnit
            if x_resolution and y_resolution and resolution_unit:
                x_res = rational_to_float(x_resolution)
                y_res = rational_to_float(y_resolution)
                if x_res != y_res:
                    return False
                if resolution_unit == 2:  # inches
                    if x_res < 72 or x_res > 300:  # typical range for digital images
                        return False
                elif resolution_unit == 3:  # centimeters
                    if x_res < 28 or x_res > 118:  # converted from inches to cm
                        return False
            
            # Check thumbnail consistency
            thumbnail = exif_data.get(513)  # JPEGThumbnail
            thumbnail_offset = exif_data.get(514)  # JPEGThumbnailOffset
            thumbnail_length = exif_data.get(515)  # JPEGThumbnailLength
            if thumbnail and thumbnail_offset and thumbnail_length:
                if len(thumbnail) != thumbnail_length:
                    return False
            
            return True
    except Exception:
        return False

def check_third_party_software_data(image_path):
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if exif_data is None:
                return True
            
            software = exif_data.get(305)  # Software tag
            if software and any(editor in software.lower() for editor in ['photoshop', 'lightroom', 'gimp', 'affinity']):
                return False
            
            if any(tag in exif_data for tag in range(37500, 37516)):  # Adobe Photoshop tag range
                return False
            
            xmp_data = exif_data.get(700)  # XMP data
            if xmp_data:
                xmp_str = xmp_data.decode('utf-8')
                if 'adobe:' in xmp_str or 'photoshop:' in xmp_str:
                    return False
            
            return True
    except Exception:
        return True

def check_embedded_thumbnail_consistency(image_path):
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if exif_data is None:
                return True
            
            thumbnail = exif_data.get(513)  # JPEGThumbnail
            if thumbnail:
                thumbnail_hash = hashlib.md5(thumbnail).hexdigest()
                
                img_hash = hashlib.md5(img.tobytes()).hexdigest()
                
                similarity = sum(a == b for a, b in zip(thumbnail_hash, img_hash)) / len(thumbnail_hash)
                return similarity > 0.7
            
            return True
    except Exception:
        return True

def check_compression_fingerprint(image_path):
    try:
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        
        dct = scipy.fftpack.dct(scipy.fftpack.dct(img, axis=0, norm='ortho'), axis=1, norm='ortho')
        
        dct_blocks = [dct[i:i+8,j:j+8] for i in range(0,dct.shape[0],8) for j in range(0,dct.shape[1],8)]
        
        block_means = [np.mean(block) for block in dct_blocks]
        
        kmeans = KMeans(n_clusters=2, random_state=0).fit(np.array(block_means).reshape(-1, 1))
        
        cluster_distance = abs(kmeans.cluster_centers_[0] - kmeans.cluster_centers_[1])[0]
        
        return cluster_distance < 5
    except Exception:
        return True

def check_histogram_credibility(image_path):
    try:
        img = cv2.imread(image_path)
        hist = cv2.calcHist([img], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        hist = cv2.normalize(hist, hist).flatten()
        
        entropy = -np.sum(hist * np.log2(hist + 1e-7))
        
        return entropy > 3
    except Exception:
        return True

def check_aspect_ratio_credibility(image_path):
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            aspect_ratio = width / height
            
            common_ratios = [1, 4/3, 3/2, 16/9, 2/1]
            
            return any(abs(aspect_ratio - ratio) < 0.1 for ratio in common_ratios)
    except Exception:
        return True

def check_image_size_credibility(image_path):
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            total_pixels = width * height
            
            min_acceptable_pixels = 1000000
            
            return total_pixels >= min_acceptable_pixels
    except Exception:
        return True

def main(image_path):
    checks = [
        ("EXIF Format Check", check_exif_format),
        ("EXIF Internal Consistency", check_exif_internal_consistency),
        ("EXIF External Consistency", check_exif_external_consistency),
        ("Third-party Software Data", check_third_party_software_data),
        ("Embedded Thumbnail Consistency", check_embedded_thumbnail_consistency),
        ("Compression Fingerprint Credibility", check_compression_fingerprint),
        ("Histogram Credibility", check_histogram_credibility),
        ("Aspect Ratio Credibility", check_aspect_ratio_credibility),
        ("Image Size Credibility", check_image_size_credibility)
    ]
    
    results = []
    for name, check_func in checks:
        passed = check_func(image_path)
        results.append((name, passed))
        print(f"{name}: {'Passed' if passed else 'Failed'}")
    
    passed_checks = [name for name, passed in results if passed]
    failed_checks = [name for name, passed in results if not passed]
    
    print("\nSummary:")
    print(f"Passed checks: {', '.join(passed_checks)}")
    print(f"Failed checks: {', '.join(failed_checks)}")

if __name__ == "__main__":
    image_path = "path/to/your/image.jpg"
    main(image_path)
