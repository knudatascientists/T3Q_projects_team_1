# ��� �ε�
import sqlite3, cv2
import streamlit as st
from PIL import Image, ImageEnhance
import requests, json, os
import numpy as np
import pandas as pd
import pydeck as pdk
import yolo_v5.detect as detect
from tkinter.tix import COLUMN
from pyparsing import empty

# ���̾ƿ� ����
st.set_page_config(layout="wide")

# �α��� ȭ��
conn = sqlite3.connect('database.db')
c = conn.cursor()

import hashlib


def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()


def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False


def create_user():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')


def add_user(username, password):
    c.execute('INSERT INTO userstable(username,password) VALUES (?,?)', (username, password))
    conn.commit()


def login_user(username, password):
    c.execute('SELECT * FROM userstable WHERE username =? AND password = ?', (username, password))
    data = c.fetchall()
    return data


def main():
    # st.title("�α��� ��� �׽�Ʈ")

    menu = ["Login", "signUp", "Dectection", "Map"]
    choice = st.sidebar.selectbox("MENU", menu)

    if choice == "Login":
        st.subheader("�α��� ���ּ���")

        username = st.sidebar.text_input("�������� �Է����ּ���")
        password = st.sidebar.text_input("��й�ȣ�� �Է����ּ���", type='password')
        if st.sidebar.checkbox("Login"):
            create_user()
            hashed_pswd = make_hashes(password)

            result = login_user(username, check_hashes(password, hashed_pswd))
            if result:

                st.success("{}������ �α����߽��ϴ�.".format(username))

            else:
                st.warning("����� �̸��̳� ��й�ȣ�� �߸��Ǿ����ϴ�.")

    elif choice == "signUp":
        st.subheader("�� ������ ����ϴ�.")
        new_user = st.text_input("�������� �Է����ּ���")
        new_password = st.text_input("��й�ȣ�� �Է����ּ���", type='password')

        if st.button("signUp"):
            create_user()
            add_user(new_user, make_hashes(new_password))
            st.success("���� ������ �����߽��ϴ�.")
            st.info("�α��� ȭ�鿡�� �α��� ���ּ���.")

    # Detection ��
    elif choice == "Dectection":
        st.subheader("���蹰 Ž��")
        selected_item = st.sidebar.radio("select", ("Image", "Video"))
        st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
        # Image ���ε� ��
        if selected_item == "Image":
            file = st.file_uploader("Upload Image", type=['jpg', 'png', 'jpeg'])
            if file != None:
                img = Image.open(file)
                img.save('./temp/temp.png', 'PNG')
                st.image(img)
                if st.button("�߷� ���"):
                    img_result, video_result = detect.run(source=f'./temp/temp.png')
                    st.image(img_result)
        # Video ���ε� ��
        elif selected_item == "Video":
            selected_video = st.radio(label="������ �������ּ���.", options=['1', '2', '3', '4'])
            st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
            if selected_video == "1":
                st.video('./temp/temp_1.mp4', start_time=0)
                if st.button("�߷� ���"):
                    # img_result, video_result = detect.run(source=f'./temp/temp_1_result.mp4')
                    st.video('./temp/temp_1_result.mp4', 'rb', start_time=0)
            elif selected_video == "2":
                st.video('./temp/temp_1.mp4', start_time=0)
                if st.button("�߷� ���"):
                    st.video('./temp/temp_1.mp4', start_time=0)
            elif selected_video == "3":
                st.video('./temp/temp_1.mp4', start_time=0)
                if st.button("�߷� ���"):
                    st.video('./temp/temp_1.mp4', start_time=0)
            elif selected_video == "4":
                st.video('./temp/temp_1.mp4', start_time=0)
                if st.button("�߷� ���"):
                    st.video('./temp/temp_1.mp4', start_time=0)


    elif choice == "Map":
        # ������ġ ��ǥ ���
        def current_location():
            here_req = requests.get("http://www.geoplugin.net/json.gp")

            if (here_req.status_code != 200):
                print("������ǥ�� �ҷ��� �� ����")
            else:
                location = json.loads(here_req.text)
                crd = {float(location["geoplugin_latitude"]), float(location["geoplugin_longitude"])}
                crd = list(crd)
                gps = pd.DataFrame([[crd[1], crd[0]]], columns=['����', '�浵'])

            return gps

        # �ʿ� ��ġ ǥ�� ------------------------------------------------------------------------------------------

        # ��ġ���� �� (��, data�� ����, �浵 �÷��� �־�� ��)

        def location_detail(data_c):
            data = data_c.copy()

            # ������ �̹��� �ҷ�����
            ICON_URL = "https://cdn-icons-png.flaticon.com/128/2268/2268142.png"
            icon_data = {
                # Icon from Wikimedia, used the Creative Commons Attribution-Share Alike 3.0
                # Unported, 2.5 Generic, 2.0 Generic and 1.0 Generic licenses
                "url": ICON_URL,
                "width": 242,
                "height": 242,
                "anchorY": 242,
            }
            data["icon_data"] = None
            for i in data.index:
                data["icon_data"][i] = icon_data
            la, lo = np.mean(data["����"]), np.mean(data["�浵"])

            layers = [
                pdk.Layer(
                    type="IconLayer",
                    data=data,
                    get_icon="icon_data",
                    get_size=4,
                    size_scale=15,
                    get_position="[�浵, ����]",
                    pickable=True,
                )
            ]

            # Deck Ŭ���� �ν��Ͻ� ����
            deck = pdk.Deck(
                map_style=None, initial_view_state=pdk.ViewState(longitude=lo, latitude=la, zoom=11, pitch=50),
                layers=layers
            )

            st.pydeck_chart(deck, use_container_width=True)

        # �ǽð� ��ġ ���� ǥ�� �Լ� ���� ------------------------------------------------------------------------
        gps = current_location()
        location_detail(gps)


if __name__ == '__main__':
    main()
