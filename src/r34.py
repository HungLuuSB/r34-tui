import random
import requests
import subprocess
import json
import http.client
from __vars__ import __headers__
from api_urls import API_URLS
from post import Post
import post


class r34Py:
    def __init__(self):
        self._session = requests.Session()
        pass

    def _get_post(self, post_id: int):
        params = [["POST_ID", str(post_id)]]
        formattedUrl = self._parseUrl(API_URLS.GET_POST.value, params)
        respone = requests.get(formattedUrl, headers=__headers__)
        res_status = respone.status_code
        res_len = len(respone.content)
        ret_post = []
        if res_status != 200 or res_len <= 0:
            return ret_post
        for post in respone.json():
            ret_post.append(Post.from_json(post))
        return (
            ret_post
            if len(ret_post) > 1
            else (ret_post[0] if len(ret_post) == 1 else ret_post)
        )

    def search(
        self, tags: list[str] = [], page_id: int = None, limit: int = 1000
    ) -> list[Post]:
        if limit < 0 or limit > 1000:
            limit = 1000
        params = [["TAGS", str("+".join(tags))], ["LIMIT", str(limit)]]
        url = API_URLS.SEARCH.value
        if page_id != None:
            url += f"&pid={{PAGE_ID}}"
            params.append(["PAGE_ID", str(page_id)])

        formattedUrl = self._parseUrl(url, params)
        curl_command = ["curl", "-s", f"{formattedUrl}"]
        response = subprocess.check_output(curl_command, text=True)

        # response = self._session.get(formattedUrl, headers=__headers__, timeout=30)
        # print(formattedUrl)
        # conn = http.client.HTTPSConnection(formattedUrl)
        # conn.request("GET", "/")
        # print(respones)
        # if len(response.content) == 0:
        #    return []

        posts = []

        for post_json in json.loads(response):
            posts.append(Post.from_json(post_json))
        return posts

    def random_post(self, tags: list = []):
        if tags != None:
            pass

    def _parseUrl(self, url: str, param: list) -> str:
        retUrl = url
        for g in param:
            key = g[0]
            value = g[1]
            retUrl = retUrl.replace("{" + key + "}", value)
        return retUrl
