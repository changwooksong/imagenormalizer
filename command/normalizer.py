# Pillow 8 이상을 확인하세요.
from re import I
import sys, math, io, os, time, json
import os.path
import shutil
from PIL import Image, ImageCms
from multiprocessing import Pool # Pool import하기

class MakeImage:
    def get_img_info(self, fileFullName):
        path_dir  = get_script_path() + '/../resource/'
        img = Image.open(path_dir + fileFullName)
        filename = self.get_file_name(fileFullName)
        res = {
                "fileFullName": fileFullName,
                "filename":filename,
                "format":img.format,
                "mode":img.mode,
                "width":img.width,
                "height":img.height,
                "dpi": self.dpiTxt(img.info),
                "rate": self.size_rate(img.width, img.height)['rate'],
                "score": self.size_rate(img.width, img.height)['score'],
                "type": self.size_rate(img.width, img.height)['type'],
                "img":img,
            }

        return res

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

    def dpiTxt(self, info):
        if 'dpi' in info:
            dpiTxt = math.ceil(info['dpi'][0])
        else:
            dpiTxt = 72
        return dpiTxt

    def get_icc(self, img):
        if 'icc_profile' in img.info:
            profile = ImageCms.getOpenProfile(io.BytesIO(img.info["icc_profile"])).tobytes()
        else:
            if img.mode != "CMYK":
                image = ImageCms.profileToProfile(img,
                                                get_script_path() + "/../color_profiles/sRGB Color Space Profile.icm",
                                                get_script_path() + "/../color_profiles/sRGB Color Space Profile.icm",
                                                renderingIntent=0)
                profile = ImageCms.getOpenProfile(io.BytesIO(image.info["icc_profile"])).tobytes()
            else:
                image = ImageCms.profileToProfile(img,
                                                get_script_path() + "/../color_profiles/USWebCoatedSWOP.icc",
                                                get_script_path() + "/../color_profiles/USWebCoatedSWOP.icc",
                                                renderingIntent=0, outputMode='CMYK')
                profile = ImageCms.getOpenProfile(io.BytesIO(image.info["icc_profile"])).tobytes()
        return profile

    def convert_image(self, img_info):
        img = img_info['img']
        path_dir  = get_script_path() + '/../300dpi/'
        tag = '300dpi'
        filename = img_info['fileFullName'].split('.')[0]
        newFileName = self.build_filename(filename, tag, img_info['format'])

        self.makeDir(path_dir)
        img.save(path_dir + newFileName, dpi=(300, 300), quality=100, format=img_info['format'], subsampling=0,
                mode=img_info['mode'], icc_profile=self.get_icc(img))

    def web_def_image(self, img_info):

        origin_img = img_info['img']
        profile = ImageCms.ImageCmsProfile(io.BytesIO(origin_img.info.get('icc_profile')))
        imgForWeb = origin_img

        if img_info['mode'] == 'CMYK':
            imgForWeb = ImageCms.profileToProfile(origin_img, profile, get_script_path() + "/../color_profiles/sRGB-IEC61966-2.1.icc", renderingIntent=0, outputMode='RGB')
            profile = ImageCms.getOpenProfile(io.BytesIO(imgForWeb.info["icc_profile"]))

        # Extract original ICC profile
        # desc = ImageCms.getProfileDescription(profile)
        # print(imgForWeb.mode)

        if (img_info['type'] == 'landscape') :
            imgForWebWidth = int(900 * img_info['width'] / img_info['height'])
            imgForWeb  = imgForWeb.resize((imgForWebWidth, 900), Image.LANCZOS)
            
        else:
            imgForWebHeight = int(900 * img_info['height'] / img_info['width'])
            imgForWeb  = imgForWeb.resize((900, imgForWebHeight), Image.LANCZOS)

        path_dir  = get_script_path() +  '/../main/'
        tag = 'for_web'

        newFileName = self.build_filename(img_info['filename'], tag, img_info['format'])
        self.makeDir(path_dir)

        imgForWeb.save(path_dir + newFileName, dpi=(72, 72), quality=95, format=img_info['format'], subsampling=0,
                mode=imgForWeb.mode, icc_propfile = profile)

    def save_size_images(self, img_info) :
        img = img_info['img']
        path_dir  = get_script_path()

        # 비율 별 사이즈 정보
        with open(path_dir + '/../size_profiles/size.json', 'r') as f:
            size_data = json.load(f)

        size_tip = size_data[img_info['rate']]

        # 이미지 명 디렉토리 생성
        dir_main = path_dir + '/../size/'
        self.makeDir(dir_main)

        filename = img_info['filename'].split('.')[0]
        dir_sub = dir_main + filename + '/'
        self.makeDir(dir_sub)

        for index, value in enumerate(size_tip) :
            size_tag  = value['name']
            width = value['width']
            height = value['height']

            if img_info['type'] == 'portrait' :
                img = img.resize((width, height), Image.ANTIALIAS)

            else :
                if img_info['rate'] != "A" and img_info['rate'] != "1:1" :
                    size_tag = size_tag.split('x') 
                    size_tag = str(size_tag[1] + 'x' + size_tag[0])

                img = img.resize((height, width), Image.ANTIALIAS)

            newFileName = self.build_filename(img_info['filename'], size_tag, img_info['format'])
            # print(newFileName)

            img.save(dir_sub + newFileName, dpi=(300, 300), quality=100, format=img_info['format'], subsampling=0,
                mode=img_info['mode'], icc_profile=self.get_icc(img_info['img']))

    def check_availability_image (self, img_info):
        # 이미지 DPI 및 사이즈 체크
        dpi = img_info['dpi']
        width = img_info['width']
        height = img_info['height']
        type = img_info['type']
        file_name = img_info['fileFullName']

        if dpi >= 200: # 200 dpi 이상
            return True

        else : # 72dpi
            if type == 'portrait':
                if width >= 2000:
                    self.convert_image(img_info)
                    return True
                else:
                    print ('[', file_name, ']', '은 해상도가 낮아 변환할 수 없습니다.')
                    return False
            else:
                if height >= 2000:
                    self.convert_image(img_info)
                    return True
                else:
                    print ('[', file_name, ']', '은 해상도가 낮아 변환할 수 없습니다.')
                    return False

    def make_converted_image(self, img_info):
        availability = self.check_availability_image(img_info)
        
        if availability == True:
            self.web_def_image(img_info)
            # self.save_size_images(img_info)
            # self.move_completed_image(img_info)
            # print('[', img_info['fileFullName'], ']', '변환 완료')

    def move_completed_image(self, img_info):
        path_dir = get_script_path()
        path_resource   = path_dir + '/../resource/' + img_info['fileFullName']
        path_completion = path_dir + '/../completion/'

        # self.makeDir(path_completion)
        # shutil.move(path_resource, path_completion + img_info['fileFullName'])


def get_start_time() :
    now = time.localtime() 
    return(time.strftime('%c', now))

def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

def converting_image_script(value) :
    format_list = ['jpg', 'jpeg','png', 'gif', 'bmp']
    file_format = value.split('.')[-1]

    if file_format in format_list:
        img = MakeImage()
        img_info = img.get_img_info(value)
        img.make_converted_image(img_info)
        # print(img_info)
    else:
        print('[', value, ']', '는 이미지 파일이 아닙니다.')



########################   스크립트 실행    ##########################
Image.MAX_IMAGE_PIXELS = None

if __name__=='__main__':
    print('=' * 100)
    print('start', ':', get_start_time()) # 작동 시작 시간 기록
    print('=' * 100)

    path_dir  = get_script_path() + '/../resource/'
    file_list = os.listdir(path_dir) # resource 파일 리스트

    if not file_list == [] : # 디렉토리에 파일이 존재
        print('File List :', file_list)
        start_time = time.time()
        pool = Pool(processes=8) # Multiprocessing
        pool.map(converting_image_script, file_list) 
        print("--- %s seconds ---" % (time.time() - start_time)) # 변환 시간 기록

    else: # 디렉토리에 파일 없음
        print('디렉토리에 변경할 이미지 파일이 없습니다.')
        sys.exit()



