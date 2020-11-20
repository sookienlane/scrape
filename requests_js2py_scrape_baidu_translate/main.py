import js2py
import requests


def translate(query):
    sign_function = js2py.eval_js(open("requests_js2py_scrape_baidu_translate/get_sign.js").read())
    url = "https://fanyi.baidu.com/basetrans"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
        "Referer": "https://fanyi.baidu.com/",
        "Cookie": "BAIDUID=714BFAAF02DA927F583935C7A354949A:FG=1; BIDUPSID=714BFAAF02DA927F583935C7A354949A; PSTM=1553390486; delPer=0; PSINO=5; H_PS_PSSID=28742_1463_21125_18559_28723_28557_28697_28585_28640_28604_28626_22160; locale=zh; from_lang_often=%5B%7B%22value%22%3A%22en%22%2C%22text%22%3A%22%u82F1%u8BED%22%7D%2C%7B%22value%22%3A%22zh%22%2C%22text%22%3A%22%u4E2D%u6587%22%7D%5D; to_lang_often=%5B%7B%22value%22%3A%22en%22%2C%22text%22%3A%22%u82F1%u8BED%22%7D%2C%7B%22value%22%3A%22zh%22%2C%22text%22%3A%22%u4E2D%u6587%22%7D%5D; REALTIME_TRANS_SWITCH=1; FANYI_WORD_SWITCH=1; HISTORY_SWITCH=1; SOUND_SPD_SWITCH=1; SOUND_PREFER_SWITCH=1; Hm_lvt_afd111fa62852d1f37001d1f980b6800=1553658863,1553766321,1553769980,1553770442; Hm_lpvt_afd111fa62852d1f37001d1f980b6800=1553770442; Hm_lvt_64ecd82404c51e03dc91cb9e8c025574=1553766258,1553766321,1553769980,1553770442; Hm_lpvt_64ecd82404c51e03dc91cb9e8c025574=1553770442"
    }
    sign = sign_function(query)
    data = {
        "query": query,
        "from": "en",
        "to": "zh",
        "token": "6f5c83b84d69ad3633abdf18abcb030d",
        "sign": sign
    }

    res = requests.post(
        url=url,
        headers=headers,
        data=data
    )
    return res.json()


if __name__ == "__main__":
    translate("I want to buy a car")