import timeimport threadingfrom common import constants as constfrom common.custom_logger import logger, DEBUG_LEVELfrom common import common_utils as utildef crop_ad(emulator_device):    util.crop_screenshot(emulator_device, const.TV_IMAGE_DIMENSIONS, const.AD_SUFFIX)def crop_close_ad(emulator_device):    util.crop_screenshot(emulator_device, const.CLOSE_AD_DIMENSIONS, const.CLOSE_AD_SUFFIX)def crop_all(emulator_device):    crop_ad(emulator_device)    crop_close_ad(emulator_device)    util.crop_menu_button(emulator_device)def take_screenshot_and_crop_all(emulator_device):    util.take_screenshot(emulator_device)    crop_all(emulator_device)def take_screenshot_and_crop_ad(emulator_device):    util.take_screenshot(emulator_device)    crop_ad(emulator_device)def take_screenshot_and_crop_close_ad(emulator_device):    util.take_screenshot(emulator_device)    crop_close_ad(emulator_device)def take_screenshot_and_crop_menu(emulator_device):    util.take_screenshot(emulator_device)    util.crop_menu_button(emulator_device)def click_on_ad(emulator_device):    logger.debug(f"[{emulator_device.serial}]: clicking AD")    emulator_device.click(const.TV_LOCATION[const.X_KEY], const.TV_LOCATION[const.Y_KEY])def click_exit_ad(emulator_device):    logger.debug(f"[{emulator_device.serial}]: exiting AD")    emulator_device.click(const.CLOSE_AD_LOCATION[const.X_KEY], const.CLOSE_AD_LOCATION[const.Y_KEY])def is_close_ad_present(emulator_device):    logger.debug(f"[{emulator_device.serial}]: Looking for AD close button")    for image in const.ORIGINAL_CLOSE_AD_IMAGES_PATHS:        if util.are_images_similar(emulator_device,                                   util.get_cropped_screenshot_path(emulator_device, const.CLOSE_AD_SUFFIX),                                   image,                                   const.CLOSE_AD_DIFF_THRESHOLD):            # This is redundant check to make sure it's not the main exit button            if not util.are_images_similar(emulator_device,                                           util.get_cropped_screenshot_path(emulator_device, const.CLOSE_AD_SUFFIX),                                           const.DONT_CLOSE_ADD_BUTTON_PATH,                                           const.CLOSE_AD_DIFF_THRESHOLD):                return True    return Falsedef is_ad_present(emulator_device):    logger.debug(f"[{emulator_device.serial}]: Looking for AD")    return util.are_images_similar(emulator_device,                                   util.get_cropped_screenshot_path(emulator_device, const.AD_SUFFIX),                                   const.ORIGINAL_TV_IMAGE_PATH,                                   const.TV_IMAGE_DIFF_THRESHOLD)def close_ad_if_playing(emulator_device):    logger.debug(f"[{emulator_device.serial}]: close ad if playing")    util.take_screenshot(emulator_device)    crop_close_ad(emulator_device)    if is_close_ad_present(emulator_device):        logger.debug(f"[{emulator_device.serial}]: closing ad")        click_exit_ad(emulator_device)        time.sleep(2)        close_ad_if_playing(emulator_device)    else:        logger.debug(f"[{emulator_device.serial}]: ad is not playing")        util.crop_menu_button(emulator_device)        if util.is_in_tavern(emulator_device):            logger.debug(f"[{emulator_device.serial}]: is in tavern")def watch_ad_and_close_after(emulator_device):    click_on_ad(emulator_device)    time.sleep(5)    close_ad_if_playing(emulator_device)def check_device_loop(emulator):    logger.info(f"Running loop for: {emulator}")    while True:        if util.is_emulator_attached(emulator):            util.take_screenshot(emulator)            crop_ad(emulator)            if is_ad_present(emulator):                logger.info(f"[{emulator.serial}]: has AD")                watch_ad_and_close_after(emulator)            else:                close_ad_if_playing(emulator)        else:            logger.error(f"[{emulator.serial}]: is offline")            breakif __name__ == '__main__':    logger.setLevel(DEBUG_LEVEL)    logger.info("Started Shakes_AD_Bot")    # check installed adb    util.check_cli_tools_installed()    adb = util.get_adb_client()    emulator_device_list = adb.device_list()    thread_list = []    if len(emulator_device_list) == 0 or (len(emulator_device_list) == 1 and emulator_device_list[0].info == const.OFFLINE):        logger.error("No running emulators, exiting now.")        exit(1)    for device in emulator_device_list:        thread = threading.Thread(target=check_device_loop, args=(device,))        thread.start()        thread_list.append(thread)    try:        while True:            pass    except KeyboardInterrupt:        logger.debug("Program status: Ending program.")        for thread in thread_list:            thread.join()