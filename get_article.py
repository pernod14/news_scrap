#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 会社環境で動くか微妙（プロキシ、日本語保存のエンコーディング問題、が想定）

import json
import csv
import ssl
import re
import urllib.request

def generate_api_url(start_date, end_date, page_num):
    '''
    newsapi.org用のAPIのURLを生成する関数
    @param start_date 記事検索の初日'2018-06-01' <- こんな感じで指定する
    @param end_date   記事検索の終日'2018-06-10' <- こんな感じで指定する
    @param page_num   1回のAPIで取得する記事本数を指定。API側の仕様上MAXは100。
    @return gen_url APIのURL
    '''
    base_url = 'https://newsapi.org/v2/everything?sources=techcrunch&language=jp'
    api_key = '&apiKey=3d024ba5e79f4f7c8e98ede1b81cf35b'
    gen_url = base_url + '&pageSize=' + str(page_num) + '&from=' + start_date + '&to=' + end_date + api_key
    return gen_url

def get_json(url):
    '''
    生成されたURLからJSONを取得してくる関数
    @param gen_url APIのURL（下のようなかんじ、ドキュメントは参照 -> https://newsapi.org/docs/endpoints/everything）
    'https://newsapi.org/v2/everything?sources=techcrunch&from=2018-06-01&to=2018-06-15&language=jp&pageSize=5&apiKey=3d024ba5e79f4f7c8e98ede1b81cf35b'
    @return json_data 記事リストのJSONファイル
    '''
    # SSL対策
    context = ssl._create_unverified_context()
    try:
        res = urllib.request.urlopen(url, context=context)
        json_data = json.loads(res.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print('HTTPError: ', e)
    except json.JSONDecodeError as e:
        print('JSONDecodeError: ', e)
    return json_data

def format_text(text):
    '''
    文中に含まれる改行とHTMLタグを消す関数
    @param text HTMLタグや改行が含まれる文章
    @return clean_text HTMLタグや改行が含まれない文章
    '''
    # 改行を消す
    tmp_text = text.replace('\r\n', '').replace('\n', '')
    # 半角カンマを読点に置換する
    tmp_text = tmp_text.replace(',', '、')
    # HTMLタグを消す
    tmp_text = tmp_text.replace('<p>', '').replace('</p>', '')
    tmp_text = re.sub('<a(.+)…', '', re.sub('<a(.+)>', '', re.sub('</a>', '', tmp_text)))
    clean_text = re.sub('<img(.+)…', '', re.sub('<img(.+)>', '', re.sub('</img>', '', tmp_text)))
    return clean_text

if __name__ == "__main__":
    # 4,5,6,7月の上中下旬ごとに最大100本ずつ記事をぬく
    # ホントは2018以外も指定できるようにすべきだが面倒なのでパス
    mnt = ['04', '05', '06', '07']
    s_day = ['01', '11', '21']
    e_day = ['10', '20', '30']
    # 1回の問い合わせで抜ける記事件数は最大100件
    page_num = 100
    with open("techcrunch_articles.csv", "w", newline="") as f:
        writer = csv.writer(f, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for m in mnt:
            for d in range(3):
                start_date = '2018-' + m + '-' + s_day[d]
                end_date = '2018-' + m + '-' + e_day[d]

                url = generate_api_url(start_date, end_date, page_num)
                json_dict = get_json(url)
                relased_page_num = json_dict['totalResults']
                data = json_dict['articles']
                # 対象期間の記事件数が100に満たない場合は、その数でループを回す
                for i in range(min(page_num, relased_page_num)):
                    if i == 0 and m == '05' and d == 0:
                        # 1行目に列名
                        writer.writerow(['date', 'title', 'description', 'url', 'author'])
                    writer.writerow([data[i]['publishedAt'], data[i]['title'], format_text(data[i]['description']), data[i]['url'], data[i]['author']])
