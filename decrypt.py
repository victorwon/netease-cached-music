#coding : utf-8
import os
import sys
import glob
import requests

DESDIR = '../cached_mp3'
LRCDIR = os.path.join(DESDIR, 'lyric')
MSCDIR = os.path.join(DESDIR, 'music')

API = 'https://api.imjad.cn/cloudmusic/?'
# two args: id  type
# type=song, lyric, comments, detail, artist, album, search
# eg  API = 'https://api.imjad.cn/cloudmusic/?type=song&id=1234132'    download music

hasModu = False
try:
    from mutagen.easyid3 import EasyID3
    from mutagen.mp3 import MP3
    hasModu = True
except:
    pass


class netease_music:
    def __init__(self, path=''):
        '''path is the direcoty that contains Music files(cached)'''
        if path == '':
            path = input('input the path of cached netease_music')
        self.path = path
        print('[+] Current Path: ' + path)
        os.chdir(path)
        self.files = glob.glob('*.uc') + glob.glob('*.uc!')
        self.id_mp = {}
        for i in self.files:
            self.id_mp[self.getId(i)] = i
        if not os.path.exists(DESDIR):
            os.mkdir(DESDIR)
        if not os.path.exists(LRCDIR):
            os.mkdir(LRCDIR)
        if not os.path.exists(MSCDIR):
            os.mkdir(MSCDIR)
        # import re
        # self.nameXpath ='//div[@class="tit"]/em[@class="f-ff2"]/text()'
        # self.lrcSentencePt=re.compile(r'\[\d+:\d+\.\d+\](.*?)\\n')         # wrong  (r'\[\d+,\d+\](\(\d+,\d+\)(\w))+\n')

    def getId(self, name):
        return name[:name.find('-')]

    def getInfoFromWeb(self, musicId):
        dic = {}
        url = API+'type=detail&id=' + musicId

        info = requests.get(url).json()['songs'][0]
        dic['artist'] = [info['ar'][0]['name']]
        dic['title'] = [info['name']]
        dic['cover'] = [info['al']['picUrl']]
        return dic

    def getInfoFromFile(self, path):
        if not os.path.exists(path):
            print('Can not find file ' + path)
            return {}
        elif hasModu:
            return dict(MP3(path, ID3=EasyID3))
        else:
            print('[Error] You can use pip3 to install mutagen or connet to the Internet')
            raise Exception('Failed to get info of ' + path)

    def getPath(self, dic,musicId):
        title = dic['title'][0]
        artist = dic['artist'][0]
        if artist in title:
            title = title.replace(artist, '').strip()
        name = (artist + ' - ' + title)
        for i in '>?*/\:"|<':
            name = name.replace(i,'-') # form valid file name
        self.id_mp[musicId] = name
        #print('''{{title: "{title}",artist: "{artist}",mp3: "http://ounix1xcw.bkt.clouddn.com/{name}.mp3",cover: "{cover}",}},'''\
               #.format(title = title,name = name,artist=artist,cover=dic['cover'][0]))
        return os.path.join(MSCDIR, name + '.mp3')
    
    def decrypt(self, cachePath):
        print(cachePath)
        musicId = self.getId(cachePath)
        print(musicId)
        idpath = os.path.join(MSCDIR, musicId + '.mp3')
        try:  # from web
            dic = self.getInfoFromWeb(musicId)
            path = self.getPath(dic,musicId)
            if os.path.exists(path): return 
            with open(path,'wb') as f:
                f.write(bytes(self._decrypt(cachePath)))
        except Exception as e:  # from file
            print(e)
            if not os.path.exists(idpath):
                with open(idpath,'wb') as f:
                    f.write(bytes(self._decrypt(cachePath)))
            dic = self.getInfoFromFile(idpath)
            path = getPath(dic,musicId)
            if os.path.exists(path):
                os.remove(idpath)
                return 
            os.rename(idpath, path)
            
    def _decrypt(self,cachePath):
        with open(cachePath, 'rb') as f:
            btay = bytearray(f.read())
        for i, j in enumerate(btay):
            btay[i] = j ^ 0xa3
        return btay
    
    def getLyric(self, musicId):
        name = self.id_mp[musicId]
        url = API + 'type=lyric&id=' + musicId
        url2 = 'https://music.163.com/api/song/lyric?id='+ musicId +'&lv=1&kv=1&tv=-1'
        try:
            lrc = requests.get(url).json()['lrc']['lyric']
            if lrc=='':
                lrc = requests.get(url2).json()['lrc']['lyric']
            if lrc=='':
                raise Exception('')
            file = os.path.join(LRCDIR, name + '.lrc')
            if not os.path.exists(file):
                with open(file, 'w', encoding='utf8') as f:
                    f.write(str(lrc))
        except Exception as e:
            print(e,' Failed to get lyric of music '+name)
    def getMusic(self):
        for ct, cachePath in enumerate(self.files):
            self.decrypt(cachePath)
            musicId = self.getId(cachePath)
            print('[{}]'.format(ct+1).ljust(5)+self.id_mp[musicId])
            self.getLyric(musicId)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        path = sys.argv[1].strip()
    else:
        path = os.path.join(os.getcwd(), 'Music1')
    handler = netease_music(path)
    handler.getMusic()
