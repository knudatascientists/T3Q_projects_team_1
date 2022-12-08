import streamlit as st 

# title ����
st.title('���� ������')
# �׳� text ���� 
st.write('�ƹ��ų� ������')
# markdown tag ���� ������
st.markdown('<h1>�±׸� �� �� �־��</h1>')
# user input �ޱ� 
st.text_input('����� �Է��� �޾ƺ�����: ')

# �̿ܿ��� �پ��� ��� ��û ����~ 
st.button 
st.sidebar 

import requests
import numpy as np

def get_cctv_url(lat, lng):
    # CCTV Ž�� ���� ������ ���� ���Ƿ� ��1 ��ŭ ����
    minX = str(lng-1)
    maxX = str(lng+1)
    minY = str(lat-1)
    maxY = str(lat+1)

    # ����key �Է�
    api_call = 'https://openapi.its.go.kr:9443/cctvInfo?' \
               'apiKey=����key' \
               '&type=ex&cctvType=2' \
               '&minX=' + minX + \
               '&maxX=' + maxX + \
               '&minY=' + minY + \
               '&maxY=' + maxY + \
               '&getType=json'

    w_dataset = requests.get(api_call).json()
    cctv_data = w_dataset['response']['data']

    coordx_list = []
    for index, data in enumerate(cctv_data):
        xy_couple = (float(cctv_data[index]['coordy']),float(cctv_data[index]['coordx']))
        coordx_list.append(xy_couple)

    # �Է��� ���浵 ��ǥ���� ���� ����� ��ġ�� �ִ� CCTV�� ã�� ����
    coordx_list = np.array(coordx_list)
    leftbottom = np.array((lat, lng))
    distances = np.linalg.norm(coordx_list - leftbottom, axis=1)
    min_index = np.argmin(distances)

    return cctv_data[min_index]


cctv_data = get_cctv_url(36.58629, 128.186793)
print('CCTV��:', cctv_data['cctvname']) # ���� ����� CCTV��
print('CCTV ���� URL:', cctv_data['cctvurl']) # ���� ����� CCTV ���� URL
