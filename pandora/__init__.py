from flask import Flask


def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        """
        只有 Hello World 的首页
        :return:
        """
        return "Hello, world!"

    # TODO: 捕获 404 错误，返回 404.html
    @app.errorhandler(404)
    def page_not_found(error):
        """
        以此项目中的404.html作为此Web Server工作时的404错误页
        """
        from flask import render_template
        return render_template("404.html"), 404

    # TODO: 完成接受 HTTP_URL 的 picture_reshape
    # TODO: 完成接受相对路径的 picture_reshape
    @app.route('/pic', methods=['GET'])
    def picture_reshape():
        """
        **请使用 PIL 进行本函数的编写**
        获取请求的 query_string 中携带的 b64_url 值
        从 b64_url 下载一张图片的 base64 编码，reshape 转为 100*100，并开启抗锯齿（ANTIALIAS）
        对 reshape 后的图片分别使用 base64 与 md5 进行编码，以 JSON 格式返回，参数与返回格式如下
        
        :param: b64_url: 
            本题的 b64_url 以 arguments 的形式给出，可能会出现两种输入
            1. 一个 HTTP URL，指向一张 PNG 图片的 base64 编码结果
            2. 一个 TXT 文本文件的文件名，该 TXT 文本文件包含一张 PNG 图片的 base64 编码结果
                此 TXT 需要通过 SSH 从服务器中获取，并下载到`pandora`文件夹下，具体请参考挑战说明
        
        :return: JSON
        {
            "md5": <图片reshape后的md5编码: str>,
            "base64_picture": <图片reshape后的base64编码: str>
        }
        """
        from requests import get
        from PIL import Image
        from flask import request
        from io import BytesIO
        from hashlib import md5
        import base64
        url = str(request.query_string, 'utf-8')
        filepath = 'tmp.png'
        if url[-1] == 'g':
            response = get(url)
            image = Image.open(BytesIO(response.content))
        else:
            with open(url, 'r') as f:
                image_src = base64.b64decode(f.read())
            with open(filepath, 'bw') as img:
                img.write(image_src)
            image = Image.open(filepath)
        image = image.resize((100, 100), Image.ANTIALIAS)
        image.save(filepath)
        md5code = md5(open(filepath,'rb').read()).hexdigest()
        base64code = base64.b64encode(open(filepath,'rb').read()).decode()
        json = {
            "md5": md5code, 
            "base64_picture": base64code
        }
        from flask import jsonify
        return jsonify(json)
            
        

    # TODO: 爬取 996.icu Repo，获取企业名单
    @app.route('/996')
    def company_996():
        """
        从 github.com/996icu/996.ICU 项目中获取所有的已确认是996的公司名单，并

        :return: 以 JSON List 的格式返回，格式如下
        [{
            "city": <city_name 城市名称>,
            "company": <company_name 公司名称>,
            "exposure_time": <exposure_time 曝光时间>,
            "description": <description 描述>
        }, ...]
        """
        from bs4 import BeautifulSoup
        from requests import get
        url = r'https://github.com/996icu/996.ICU/tree/master/blacklist'
        result = get(url)
        soup = BeautifulSoup(result.text, 'lxml')
        box_body = soup.find('div',attrs={"class":"Box-body"})
        table = box_body.find_all('table')[1]
        tr_all = table.find_all('tr')
        JSON_List = []
        for tr in tr_all:
            tds = tr.find_all('td')
            if len(tds) == 0:
                continue
            json = {
                "city": tds[0].string,
                "company": tds[1].string,
                "exposure_time": tds[2].string,
                "description": tds[3].string
                }
            JSON_List.append(json)
        from flask import jsonify
        app.config['JSON_AS_ASCII'] = False
        return jsonify(JSON_List)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
