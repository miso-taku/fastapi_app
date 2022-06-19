import streamlit as st
import requests
import datetime
import json
import pandas as pd

def main():
    page = st.sidebar.selectbox('Chose your page', ['users', 'rooms', 'booking'])

    func_dict.get(page, select_err)()


def test_users():
    st.title('ユーザー登録画面')

    with st.form(key='user'):
        # user_id: int = random.randint(0, 10)
        username: str = st.text_input('ユーザー名', max_chars=15)
        data = {
            # 'user_id': user_id,
            'username': username
        }
        submit_button = st.form_submit_button(label="ユーザー登録")

    if submit_button:
        url = 'http://127.0.0.1:8000/users'
        res = requests.post(url, json.dumps(data))
        if res.status_code == 200:
            st.success('ユーザー登録完了')
        st.json(res.json())


def test_rooms():
    st.title('会議室登録画面')

    with st.form(key='rooms'):
        # room_id: int = random.randint(0, 10)
        room_name: str = st.text_input('部屋名', max_chars=10)
        capacity: int = st.number_input('定員', step=1)
        data = {
            # 'room_id': room_id,
            'room_name': room_name,
            'capacity': capacity
        }
        submit_button = st.form_submit_button(label="会議室登録")

    if submit_button:
        url = 'http://127.0.0.1:8000/rooms'
        res = requests.post(url, json.dumps(data))
        if res.status_code == 200:
            st.success('会議室登録完了')        
        st.json(res.json())


def test_booking():
    st.title('会議室予約画面')
    # ユーザー一覧の取得
    url_users = 'http://127.0.0.1:8000/users'
    res = requests.get(url_users)
    users = res.json()
    # Key:username value:user_idの辞書型
    users_name = {}
    for user in users:
        users_name[user['username']] = user['user_id']

    # 会議室一覧の取得
    url_rooms = 'http://127.0.0.1:8000/rooms'
    res = requests.get(url_rooms)
    rooms = res.json()
    rooms_name = {}
    for room in rooms:
        rooms_name[room['room_name']] = {
            'room_id': room['room_id'],
            'capacity': room['capacity']
        }
    
    st.write('### 会議室一覧')
    df_rooms = pd.DataFrame(rooms)
    df_rooms.columns = ['会議室名', '定員', '会議室ID']
    st.table(df_rooms)

    # 予約一覧の取得
    url_bookings = 'http://127.0.0.1:8000/bookings'
    res = requests.get(url_bookings)
    bookings = res.json()

    df_bookings = pd.DataFrame(bookings)
    users_id = {}
    for user in users:
        users_id[user['user_id']] = user['username']
    rooms_id = {}
    for room in rooms:
        rooms_id[room['room_id']] = {
            'room_name': room['room_name'],
            'capacity': room['capacity'],
        }

    # IDを各値に変更
    to_username = lambda x: users_id[x]
    to_room_name = lambda x: rooms_id[x]['room_name']
    to_datetime = lambda x: datetime.datetime.fromisoformat(x).strftime('%Y/%m/%d %H:%M')

    # 特定の列に適用
    df_bookings['user_id'] = df_bookings['user_id'].map(to_username)
    df_bookings['room_id'] = df_bookings['room_id'].map(to_room_name)
    df_bookings['start_datetime'] = df_bookings['start_datetime'].map(to_datetime)
    df_bookings['end_datetime'] = df_bookings['end_datetime'].map(to_datetime)

    df_bookings = df_bookings.rename(columns={
        'user_id': '予約者名',
        'room_id': '会議室名',
        'booked_num': '予約人数',
        'start_datetime': '開始日時',
        'end_datetime': '終了日時',
        'booking_id': '予約番号'
    })
    
    st.write('### 予約一覧')
    st.table(df_bookings)

    

    with st.form(key='booking'):
        # booking_id: int = random.randint(0, 10)
        username: str = st.selectbox('予約者名', users_name.keys())
        room_name: str = st.selectbox('会議室名', rooms_name.keys())

        booked_num = st.number_input('予約人数', step=1, min_value=1)
        date = st.date_input('日付:', min_value=datetime.date.today())
        start_time = st.time_input('開始時刻:', value=datetime.time(hour=9, minute=0))
        end_time = st.time_input('終了時刻:', value=datetime.time(hour=20, minute=0))

        submit_button = st.form_submit_button(label="予約登録")

    if submit_button:
        user_id: int = users_name[username]
        room_id: int = rooms_name[room_name]['room_id']
        capacity: int = rooms_name[room_name]['capacity']
        data = {
            'user_id': user_id,
            'room_id': room_id,
            'booked_num': booked_num,
            'start_datetime': datetime.datetime(
                year=date.year,
                month=date.month,
                day=date.day,
                hour=start_time.hour,
                minute=start_time.minute
            ).isoformat(),
            'end_datetime': datetime.datetime(
                year=date.year,
                month=date.month,
                day=date.day,
                hour=end_time.hour,
                minute=end_time.minute
            ).isoformat()
        }
    
        # 定員より多いの予約人数
        if booked_num > capacity:
            st.error('予約人数が多すぎます。')
            st.error(f'{room_name}の定員{capacity}名に対して{booked_num}名の予約をしています。')
        # 開始時刻が終了時刻以降
        elif start_time >= end_time:
            st.error('開始時刻が終了時刻を超えています。')
        else:
            # 会議室予約
            # st.json(data)
            url = 'http://127.0.0.1:8000/bookings'
            res = requests.post(url, json.dumps(data))
            if res.status_code == 200:
                st.success('予約完了')
            st.write(res.status_code)
            st.json(res.json())

        
def select_err():
    st.error('ERROR')

func_dict = {
    'users': test_users,
    'rooms': test_rooms,
    'booking': test_booking
}

if __name__ =='__main__':
    main()