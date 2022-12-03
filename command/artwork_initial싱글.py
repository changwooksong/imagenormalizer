# Pillow 8 이상을 확인하세요.
from re import I
import sys, math, io, os, time
from PIL import Image, ImageCms
import os.path



class MakeImage:
    def get_file_name(self, fileFullName):
        filename = fileFullName.split('_') 
        filename = str(filename[0] + '_' + filename[1])

        return filename

    def build_filename(self, filename, tag, imgformat):
        if imgformat == "JPEG": ext = "jpg"
        elif imgformat == "PNG": ext = "png"
        elif format == "GIF": ext = "gif"
        elif format == "BMP": ext = "bmp"
        else: ext = "ext"
        newfname = filename + "_" + str(tag) + "." + ext

        return newfname

    def makeDir(self, dir):
        if not(os.path.isdir(dir)):
            os.mkdir(os.path.join(dir))

    def get_script_path(self):
        return os.path.dirname(os.path.realpath(sys.argv[0]))

    def size_rate(self, width, height):
        if width >= height:
            type = "landscape"
        else:
            type = "portrait"
        rateval = max(width,height) / min(width,height)
        dataset = {"1:1":abs(rateval-1.0),
                "5:4":abs(rateval-1.25),
                "4:3":abs(rateval-1.33),
                "3:2":abs(rateval-1.50),
                "A":abs(rateval-1.41)}
        res = {"rate": min(dataset, key=dataset.get),
            "score": dataset[min(dataset, key=dataset.get)],
            "type":type}
        return res

    def dpiTxt(self, imginfo):
        if 'dpi' in imginfo:
            dpiTxt = math.ceil(imginfo['dpi'][0])
        else:
            dpiTxt = 72
        return dpiTxt

    def get_icc(self, img):
        if 'icc_profile' in img.info:
            profile = ImageCms.getOpenProfile(io.BytesIO(img.info["icc_profile"])).tobytes()
        else:
            if img.mode != "CMYK":
                image = ImageCms.profileToProfile(img,
                                                self.get_script_path() + "/../color_profiles/sRGB Color Space Profile.icm",
                                                self.get_script_path() + "/../color_profiles/sRGB Color Space Profile.icm",
                                                renderingIntent=0)
                profile = ImageCms.getOpenProfile(io.BytesIO(image.info["icc_profile"])).tobytes()
            else:
                image = ImageCms.profileToProfile(img,
                                                self.get_script_path() + "/../color_profiles/USWebCoatedSWOP.icc",
                                                self.get_script_path() + "/../color_profiles/USWebCoatedSWOP.icc",
                                                renderingIntent=0, outputMode='CMYK')
                profile = ImageCms.getOpenProfile(io.BytesIO(image.info["icc_profile"])).tobytes()
        return profile

    def convert_image(self, filename, imgOrigin, imgFormat, imgMode):
        dir = './300dpi/'
        tag = 'covert_300dpi'
        newFileName = self.build_filename(filename, tag, imgFormat)

        self.makeDir(dir)

        imgOrigin.save("./300dpi/" + newFileName, dpi=(300, 300), quality=100, format=imgFormat, subsampling=0,
                mode=imgMode, icc_profile=self.get_icc(imgOrigin))

    def web_def_image(self, filename, imgOrigin, imgWidth, imgHeight, imgRatio, imgFormat):

        if (imgRatio == 'landscape') :
            imgForWebHeihgt = int(900 * imgHeight / imgWidth)
            imgForWeb  = imgOrigin.resize((900, imgForWebHeihgt), Image.ANTIALIAS)
            
        else:
            imgForWebWidth = int(900 * imgWidth / imgHeight)
            imgForWeb  = imgOrigin.resize((imgForWebWidth, 900), Image.ANTIALIAS)

        dir = './main/'
        tag = 'for_web'
        
        newFileName = self.build_filename(filename, tag, imgFormat)

        self.makeDir(dir)

        imgForWeb.save(dir + newFileName, dpi=(72, 72), quality=95, format=imgFormat, subsampling=0,
                mode="RGB", icc_profile=self.get_icc(imgOrigin))

    def save_a_size_images(self, filename, imgOrigin, imgWidth, imgHeight, imgRatio, imgFormat, imgMode) :
        sizeTip = [ (9933, 14043), (7016, 9933), (4960, 7016),  (3508, 4960), (2480, 3508) ]

        img = imgOrigin

        dir = './size/'
        self.makeDir(dir)

        for index, value in enumerate(sizeTip):

            if imgRatio == 'landscape' :
                img  = img.resize((value[1], value[0]), Image.ANTIALIAS)
            else :
                img  = img.resize((value[0], value[1]), Image.ANTIALIAS)

            tag = 'A' + str(index)
            newFileName = self.build_filename(filename, tag, imgFormat)

            img.save(dir + newFileName, dpi=(300, 300), quality=100, format=imgFormat, subsampling=0,
                mode=imgMode, icc_profile=self.get_icc(imgOrigin))

    def get_imginfo(self, path_dir, fileFullName, filename):

        img = Image.open(path_dir + fileFullName)

        res = {
                "filename":filename,
                "format":img.format,
                "mode":img.mode,
                "width":img.width,
                "height":img.height,
                "dpi": self.dpiTxt(img.info),
                "img":img
            }

        return res

    def make_img_all (self, fileFullName, filename, imgOrigin, imgWidth, imgHeight, imgRatio, imgFormat, imgDPI, imgMode):
        if imgDPI != 300:
            self.convert_image(filename, imgOrigin, imgFormat, imgMode)

            # img_t = img.get_imginfo(img.build_filename(filename, img.infoImg['format'],"to_300dpi"))
            # conv_filename = img_t["filename"]
            # conv_format = img_t["format"]
            # conv_mode = img_t["mode"]
            # conv_width = img_t["width"]
            # conv_height = img_t["height"]
            # conv_dpi = img_t["dpi"]

            print ('원본이 72dpi 입니다.')

        else:
            print ('원본이 300dpi 입니다')

        self.web_def_image(filename, imgOrigin, imgWidth, imgHeight, imgRatio, imgFormat)
        self.save_a_size_images(filename, imgOrigin, imgWidth, imgHeight, imgRatio, imgFormat, imgMode)    
        


########################   스크립트 실행    ##########################
Image.MAX_IMAGE_PIXELS = None

# 디렉토리 내 파일 리스트
path_dir = './source/'
file_list = os.listdir(path_dir)

start_time = time.time()

for index, value in enumerate(file_list):
    img = MakeImage()

    fileFullName = value
    filename = img.get_file_name(value)
    imgInfo  = img.get_imginfo(path_dir, fileFullName, filename)
    imgOrigin = imgInfo['img']
    imgWidth  = imgInfo['width']
    imgHeight = imgInfo['height']
    imgRatio  = img.size_rate(imgWidth, imgHeight)
    imgFormat = imgInfo['format']
    imgDPI    = imgInfo['dpi']
    imgMode   = imgInfo['mode']

    # print(imgInfo['mode'])

    # attr = [fileFullName, filename, imgOrigin, imgWidth, imgHeight, imgRatio, imgFormat, imgDPI]

    img.make_img_all(fileFullName, filename, imgOrigin, imgWidth, imgHeight, imgRatio, imgFormat, imgDPI, imgMode)


print("--- %s seconds ---" % (time.time() - start_time))



# print(
#     str(infoImg['filename']) + "\t"
#     + str(infoImg['format']) + "\t"
#     + infoImg['mode'] + "\t"
#     + str(infoImg['width']) + "\t"
#     + str(infoImg['height']) + "\t"
#     + size_rate(infoImg['width'],infoImg['height'])["type"] + "\t"
#     + size_rate(infoImg['width'],infoImg['height'])["rate"] + "\t"
#     + str(size_rate(infoImg['width'],infoImg['height'])["score"]) + "\t"
#     + str(dpiTxt(infoImg['img'].info)) + "\t"
#     + conv_filename + "\t"
#     + conv_format + "\t"
#     + conv_mode + "\t"
#     + str(conv_width) + "\t"
#     + str(conv_height) + "\t"
#     + str(conv_dpi)
# )


