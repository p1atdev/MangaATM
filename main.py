import requests
import re
from pathlib import Path
from bs4 import BeautifulSoup
import os
# import numpy as np

#漫画をダウンロードする関数
def download(imgs, path):
    output_folder = Path(path)
    output_folder.mkdir(exist_ok=True)

    #gifの除外
    for index, img in enumerate(imgs):
        imageURL = img["src"]

        #もしgifなら
        if (imageURL.endswith(".gif")):
            imgs.pop(index) #削除

    #画像のダウンロード
    for index, img in enumerate(imgs):
        # print("画像URL：", img)
        imageURL = img["src"]

        imagePath = output_folder.joinpath(str(index)+str('.jpeg'))
        image = requests.get(imageURL)

        open(imagePath, 'wb').write(image.content)

    print("ダウンロード完了")

# ループする
while(True):

    #URLの入力
    print("URLを入力してください")
    args = input().split(" ")
    url = args[0]

    #ダウンロードするパス
    download_path = "./"

    try:
        # FIXME: ここをなおせ
        if (args[1] != None):
            #パスを指定
            download_path = args[1]

    except:
        print("pathの指定なし")

    # 漫画のURlか一覧のURLか判定する
    # htmlを取得

    #一覧のURLの場合
    if ("mangabank.org/channel/" in url):
        #リンクの集合体
        links = []

        for i in range(100):
            # 全ての漫画のURLを入手する

            response = requests.get(url + "page/" + str(i+1))
            soup = BeautifulSoup(response.text,'lxml')

            #404か判定
            try:
                message404 = soup.find("h3", class_="errortitle")
                if (message404 != None):
                    #404なのでブレイク
                    break
            except:
                print("404ではない")

            # 404ではないので漫画のURLを入手する
            mangaName = soup.find('h2', class_='entry-title').string.replace("\n", "").replace("\t", "")
            # print("漫画のタイトル：", mangaName)    #タイトル
            # print("ページ：", i+1)

            #リンクを取得
            linkObj = soup.find_all('a',rel=re.compile('bookmark'))
            # print(linkObj)
            
            # 元のリンクと結合
            for link in linkObj:
                links = links + [link["href"]]

        # 親ファイルの作成のためにタイトルを取得
        response = requests.get(url)
        soup = BeautifulSoup(response.text,'lxml')
        title = soup.find('h2', class_='entry-title').string.replace("\n", "").replace("\t", "")
        print("ダウンロード中：", title)    #タイトル
        #親ディレクトリを作成
        os.makedirs(download_path + title, exist_ok=True)


        #まとめてダウンロードのために親ファイルを作成
        download_path = download_path + title + "/"
        print("親ディレクトリ：", download_path)

        # TODO:linkの配列を逆向きにする
        for i in range(len(links) // 2):
            links[i],links[-1-i] = links[-1-i],links[i]

        # 画像のurlを持ってくる
        for link in links:
            # print(link)
            response = requests.get(link)
            soup = BeautifulSoup(response.text,'lxml')
            title = soup.find('h1', class_='entry-title').string.replace("\n", "").replace("\t", "")
            print("漫画のタイトル：", title)    #タイトル

            #ダウンロードパスの更新
            download_current_path = Path(download_path + title)

            #画像
            imgs = soup.find_all('img',src=re.compile('^https://ssl.'))

            # print("画像s：", imgs)

            #ダウンロード
            download(imgs, download_current_path)


    elif "https://mangabank.org/" in url :
        response = requests.get(url)
        soup = BeautifulSoup(response.text,'lxml')
        title = soup.find('h1', class_='entry-title').string.replace("\n", "").replace("\t", "")
        # print("漫画のタイトル：", title)    #タイトル

        #ダウンロードパスの更新
        download_current_path = Path(download_path + title)

        #画像
        imgs = soup.find_all('img',src=re.compile('^https://ssl.'))

        #ダウンロード
        download(imgs, download_current_path)

    else:
        print("正しいURLを入力してください")        
