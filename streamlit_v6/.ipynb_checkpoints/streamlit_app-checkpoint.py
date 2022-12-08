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
from geopy.geocoders import Nominatim
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode

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
        option = st.sidebar.selectbox(
            '� ������ ���ðڽ��ϱ�?',
            ('�뱸 ��ü','�ϱ�', '�߱�', '����', '����',"����", "������", "�޼���", "�޼���"))   
        
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
            ICON_URL = "https://cdn-icons-png.flaticon.com/512/2711/2711648.png"
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
            
            
            if len(data_c) == 0:
                pass
            else:
                # Deck Ŭ���� �ν��Ͻ� ����
                deck = pdk.Deck(height=100,
                                #width=1000,
                                map_style='road', 
                                initial_view_state=pdk.ViewState(longitude=lo, 
                                                                latitude=la, 
                                                                zoom=12, 
                                                                pitch=50), 
                                layers=layers,
                                tooltip={"text":"{�ּ�}\n{����}/{�浵}"})

                st.pydeck_chart(deck, use_container_width=True)
                
        # [ gps �����ͼ� ���� �� ���� �Լ� ]--------------------------------------------------
        def add_gps_all(gps):
            # gps_all(����) �ҷ�����
            gps_all = pd.read_csv('gps_all.csv')

            # gps_all(����), gps(�߰� ����) ������������ ���� 
            gps_all = pd.concat([gps_all,gps]).reset_index()
            gps_all = gps_all.drop('index',axis=1)

            # �ߺ� ��ġ���� ����
            gps_all = gps_all.drop_duplicates(['����','�浵'])

            # �߰� ��ġ���� ����� ������������ ����
            gps_all.to_csv('gps_all.csv',index = False)
            
        # [����,�浵 -> �ּ� ��ȯ �Լ�]-----------------------------------------------------    
        def geocoding_reverse(lat_lng_str): 
            geolocoder = Nominatim(user_agent = 'South Korea', timeout=None)
            address = geolocoder.reverse(lat_lng_str)

            return address            
                
        # [ ���� ���� �ּ� ������������ �Լ� ]----------------------------------------------------
        def createDF(gps_all):
        # ����,�浵 -> �ּ� ��ȯ
            address_list = []
            for i in range(len(gps_all)):

                lat = gps_all['����'][i]
                lng = gps_all['�浵'][i]
                address = geocoding_reverse(f'{lat}, {lng}')

                # ī�װ� ���� 
                if option =='�뱸 ��ü':
                    address_list.append(address)
                elif option in address[0]:
                    address_list.append(address)

            df = pd.DataFrame(address_list, columns=['�ּ�','��ġ����(����,�浵)'])

            df_map = pd.DataFrame(columns=['�ּ�','����','�浵'])
            for i in range(len(df)):
                df_map.loc[i] = [df.loc[i]['�ּ�'],df.loc[i][1][0],df.loc[i][1][1]]

            # ����,�浵 �ּҺ�ȯ ������������ �ð�ȭ
            # st.dataframe(df)

            # �ش� ���� ��ġ���� ���� ǥ��
            st.write(option,'����, ������ �ʿ��� ����: ',len(df),'��')

            return df_map                

        # [ ���� �Լ� ���� �ڵ� ]------------------------------------------------------------------------

        # �ǽð� ��ġ���� ����
        gps = current_location()

        # ���� ��ġ���������Ϳ� �ǽð� ��ġ���� �߰� ����
        add_gps_all(gps)

        # ���� ������ ��ü ��ġ���� ���� �ҷ�����
        gps_all = pd.read_csv('gps_all.csv')

        # �ּ� ������������ ǥ��
        df_map = createDF(gps_all) 
        # ��ü ��ġ���� �� ������ ǥ��
        location_detail(df_map)
        
        def aggrid_interactive_table(df):
            options = GridOptionsBuilder.from_dataframe(
                df,  enableRowGroup=True, enableValue=True, enablePivot=True
            )
            options.configure_side_bar()

            options.configure_selection('single')
            selection = AgGrid(
                df,
                enable_enterprise_modules=True,
                gridOptions=options.build(),
                update_mode=GridUpdateMode.MODEL_CHANGED,
                allow_unsafe_jscode=True,
            )

            return selection

        col1, col2 = st.columns(2)
        with col1:
            selection = aggrid_interactive_table(df_map)
        with col2:
            try:
                if selection:
                # df ��/�浵 �̱�
                    #st.write("������ �ʿ��� ��ƮȦ")
                    #st.write('����: ', selection['selected_rows'][0]['����'], '�浵: ', selection['selected_rows'][0]['�浵'])
                    if selection['selected_rows'][0]['����'] == 35.812507:
                        img=Image.open(r'.\result\1.jpg')
                        st.image(img)
                    if selection['selected_rows'][0]['����'] == 35.832596089:
                        img=Image.open(r'.\result\2.jpg')
                        st.image(img)
                    if selection['selected_rows'][0]['����'] == 35.88249341:
                        img=Image.open(r'.\result\3.jpg')
                        st.image(img)
                    if selection['selected_rows'][0]['����'] == 35.86262305:
                        img=Image.open(r'.\result\4.jpg')
                        st.image(img)
                    if selection['selected_rows'][0]['����'] == 35.8428000942:
                        img=Image.open(r'.\result\5.jpg')
                        st.image(img)
                    if selection['selected_rows'][0]['����'] == 35.8723688469:
                        img=Image.open(r'.\result\7.jpg')
                        st.image(img)
                    if selection['selected_rows'][0]['����'] == 35.8920472:
                        img=Image.open(r'.\result\8.jpg')
                        st.image(img)
            except:
                pass

if __name__ == '__main__':
    main()
