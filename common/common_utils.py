import os

import adbutils
import subprocess
import time
from PIL import Image, ImageEnhance
import pytesseract

from common import constants as const
from common.custom_logger import logger
from common.image_comparator import CompareImage


def check_cli_tools_installed():
    try:
        adb_command = "adb --version"
        result = subprocess.run(adb_command, shell=True, capture_output=True)
        if "Android Debug Bridge" in str(result.stdout):
            logger.debug("ADB is installed.")
        else:
            raise Exception
    except Exception:
        logger.warning("ADB is not installed. Please use: brew install android-platform-tools")
        exit(1)

    try:
        convert_command = "convert --version"
        result = subprocess.run(convert_command, shell=True, capture_output=True)
        if "Version: ImageMagick" in str(result.stdout):
            logger.debug("Convert is installed.")
        else:
            raise Exception
    except Exception:
        logger.warning("Convert is not installed. Please install")
        exit(1)


def is_emulator_attached(emulator_device):
    if emulator_device.info[const.STATE_KEY] == "device":
        logger.debug(f"[{emulator_device.serial}] is attached")
        return True
    else:
        logger.error(f"[{emulator_device.serial}] IS OFFLINE")
        exit(1)


def get_adb_client():
    return adbutils.AdbClient(host="127.0.0.1", port=5037)


def to_box(dimensions):
    return dimensions['left'], dimensions['top'], dimensions['right'], dimensions['bottom']


def get_screenshot_path(emulator_device):
    return const.SCREENSHOT_PATH_PREFIX + emulator_device.serial + const.IMAGE_EXTENSION


def get_cropped_screenshot_path(emulator_device, suffix=""):
    suffix = "-" + suffix if suffix != "" else ""
    return const.CROPPED_SCREENSHOT_PATH_PREFIX + emulator_device.serial + suffix + const.IMAGE_EXTENSION


def take_screenshot(emulator_device):
    logger.info(f"[{emulator_device.serial}] Taking a screenshot")

    start_time = time.time()

    adb_command = f"adb -s {emulator_device.serial} exec-out screencap -p > {get_screenshot_path(emulator_device)}"
    subprocess.run(adb_command, shell=True, check=True)

    logger.debug(f"[{emulator_device.serial}] Execution of sceenshot took: {time.time() - start_time:.6f} seconds")


def crop_screenshot(emulator_device, dimensions, suffix):
    logger.debug(f"[{emulator_device.serial}] Cropping a screenshot")
    start_time = time.time()

    # Image.open(get_screenshot_path(emulator_device)).crop(to_box(dimensions)).save(get_cropped_screenshot_path(emulator_device))
    crop_cmd = f"convert {get_screenshot_path(emulator_device)} -crop {dimensions['right'] - dimensions['left']}x{dimensions['bottom'] - dimensions['top']}+{dimensions['left']}+{dimensions['top']} {get_cropped_screenshot_path(emulator_device, suffix)}"
    subprocess.run(crop_cmd, shell=True, check=True)

    logger.debug(f"[{emulator_device.serial}] Execution of cropping took: {time.time() - start_time:.6f} seconds")


def are_images_similar(emulator_device, first_image, second_image, threshold):
    start_time = time.time()  # Record the start time

    compare_image = CompareImage(first_image, second_image)
    image_difference = compare_image.compare_image()
    logger.debug(f"[{emulator_device.serial}]: Compared ({first_image.split('/')[-1]}) X ({second_image.split('/')[-1]}) difference: {image_difference}")

    logger.debug(f"[{emulator_device.serial}]: Execution of comparing took: {time.time() - start_time:.6f} seconds")

    return image_difference < threshold


def crop_menu_button(emulator_device):
    crop_screenshot(emulator_device, const.MENU_BUTTON_IMAGE_DIMENSIONS, const.MENU_BUTTON_SUFFIX)


def is_in_tavern(emulator_device):
    logger.debug(f"[{emulator_device.serial}]: Looking for menu button")

    if are_images_similar(emulator_device,
                           get_cropped_screenshot_path(emulator_device, const.MENU_BUTTON_SUFFIX),
                           const.ORIGINAL_MENU_BUTTON_NOTIFICATION_IMAGE_PATH,
                           const.MENU_BUTTON_IMAGE_DIFF_THRESHOLD):
        logger.debug(f"[{emulator_device.serial}]: You have a notification")

        return True

    return are_images_similar(emulator_device,
                              get_cropped_screenshot_path(emulator_device, const.MENU_BUTTON_SUFFIX),
                              const.ORIGINAL_MENU_BUTTON_IMAGE_PATH,
                              const.MENU_BUTTON_IMAGE_DIFF_THRESHOLD)



def get_npc_image_path(npc_name):
    return os.path.join(const.ORIGINAL_NPC_DIR_PATH, npc_name) + const.IMAGE_EXTENSION


def get_contrasted_image_path(image_path):
    return image_path.split(const.IMAGE_EXTENSION)[0] + "_contrasted" + const.IMAGE_EXTENSION


def enhance_image_contrast(image_path):
    start_time = time.time()
    image = Image.open(image_path)
    im_output = ImageEnhance.Contrast(image).enhance(3)
    im_output.save(get_contrasted_image_path(image_path))
    print(f"Execution of contrast enhancing: {time.time() - start_time:.6f} seconds")


def get_number_from_image(image_path):
    enhance_image_contrast(image_path)
    image = Image.open(get_contrasted_image_path(image_path))
    text = pytesseract.image_to_string(image, config='--psm 6')

    if "," in text:
        numeric_text = text.replace("\n", "").replace(",", ".")
        return float(numeric_text)

    elif ":" in text:
        numeric_text = text.replace("\n", "").split(":")
        return (int(numeric_text[0]) * 60) + int(numeric_text[1])

    else:
        return int(''.join(filter(str.isdigit, text)))

