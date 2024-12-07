import pandas as pd
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os, sys
import re

def create_object_from_db(to_return, callback, group, column_name=None, exam=None):
    try:
        path = os.path.join(os.path.dirname(sys.argv[0]), 'db_groups', f'{group}db.xlsx')
        df = pd.read_excel(path)

        if (to_return == 'keyboard' and column_name == 'Время'):
            list = df[column_name].drop_duplicates().tolist()
            list = df.query(f"Экзамен == '{exam}'")
            keyboard = InlineKeyboardMarkup()
            for option in list.itertuples(index=False, name=None):
                keyboard.row(InlineKeyboardButton(str(option[1]), callback_data=str(callback) + '_' + str(option[1])))
            keyboard.row(InlineKeyboardButton('Домой', callback_data='start'))
            return keyboard

        if (to_return == 'keyboard' and column_name == 'Экзамен'):
            list = df.drop_duplicates(subset=['Экзамен'])
            keyboard = InlineKeyboardMarkup()
            for option in list.itertuples(index=False, name=None):
                keyboard.row(InlineKeyboardButton(str(option[0]),
                                                  callback_data=str(callback) + '_' + str(option[0])))
            keyboard.row(InlineKeyboardButton('Домой', callback_data='start'))
            return keyboard

        if (to_return == 'keyboard'):
            keyboard = InlineKeyboardMarkup()
            exam_time_list = df.values.tolist()
            for exam, time in exam_time_list:
                keyboard.row(InlineKeyboardButton(f"{exam}: {time}",
                                                  callback_data=callback + '_' + f"{exam}_{time}"))
            keyboard.row(InlineKeyboardButton('Домой', callback_data='start'))
            return keyboard

        if (to_return == 'list'):
            return list

        if (to_return == 'exam_times'):
            filtered_df = df[df['Экзамен'] == exam]
            times_list = filtered_df['Время'].tolist()
            return times_list

        else:
            return

    except FileNotFoundError:
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton('Домой', callback_data='start'))
        return keyboard

def create_keyboard_from_dir(dirname, callback):
    path = os.path.join(os.path.dirname(sys.argv[0]), f'{dirname}')
    keyboard = InlineKeyboardMarkup()

    if ('db' in dirname):
        list = [os.path.splitext(filename)[0][:-2] for filename in os.listdir(path)
                if os.path.isfile(os.path.join(path, filename))]
        for option in list:
            keyboard.row(InlineKeyboardButton(option, callback_data=callback + '_' + option))
        keyboard.row(InlineKeyboardButton('Домой', callback_data='start'))
        return keyboard

    # Получение названий файлов без расширений
    list = [os.path.splitext(filename)[0] for filename in os.listdir(path)
            if os.path.isfile(os.path.join(path, filename))]

    for option in list:
        keyboard.row(InlineKeyboardButton(option, callback_data=callback + '_' + option))
    keyboard.row(InlineKeyboardButton('Домой', callback_data='start'))
    return keyboard


def create_keyboard_from_list(list, callback):
    keyboard = InlineKeyboardMarkup()
    for option in list:
        keyboard.row(InlineKeyboardButton(option, callback_data=callback + '_' + option))
    keyboard.row(InlineKeyboardButton('Домой', callback_data='start'))
    return keyboard


def get_students(group):
    path = os.path.join(os.path.dirname(sys.argv[0]), 'list_student', f'{group}.txt')
    with open(path, 'r', encoding='utf-8') as file:
        student_list = file.readlines()
    student_list = [line.strip() for line in student_list]
    return student_list


def final_record(user):
    path = os.path.join(os.path.dirname(sys.argv[0]), 'final_record', f'{user[0]}.xlsx')
    if os.path.exists(path):
        # Читаем существующий файл
        df = pd.read_excel(path)
    else:
        # Создаем новый DataFrame с заданными столбцами
        df = pd.DataFrame([user], columns=['Группа', 'Экзамен', 'Время', 'ФИО'])
        df.to_excel(path, index=False)
        return

    # Объединяем существующий DataFrame с новым
    user = pd.DataFrame([user], columns=['Группа', 'Экзамен', 'Время', 'ФИО'])
    combined_df = pd.concat([df, user], ignore_index=True).reset_index(drop=True)
    # Удаляем дубликаты, оставляя последнее вхождение
    combined_df = combined_df.drop_duplicates(keep='last')
    combined_df.to_excel(path, index=False)


def watch_students(group, exam):
    path = os.path.join(os.path.dirname(sys.argv[0]), 'final_record', f'{group}.xlsx')
    try:
        df = pd.read_excel(path)
        df = df.query(f"Экзамен == '{exam}'").sort_values(by=['Время', 'ФИО'])
        is_df_empy = df.empty
        df = df.to_string(index=False)
        if is_df_empy == True:
            return 'Пока никто не записался на экзамен :_('
        else:
            return df
    except FileNotFoundError:
        return 'Пока никто не записался на экзамен :_('


def change_exam_list_for_groups(action, group=None, exam=None, time=None):
    path = os.path.join(os.path.dirname(sys.argv[0]), 'db_groups', f'{group}db.xlsx')
    andpath = os.path.join(os.path.dirname(sys.argv[0]), 'final_record', f'{group}.xlsx')

    if (action == 'remove'):
        df = pd.read_excel(path)
        condition = (df['Экзамен'] == f'{exam}') & (df['Время'] == f'{time}')
        # Удаление строки, удовлетворяющей условию
        df = df.drop(df[condition].index)
        df.to_excel(path, index=False)
        try:
            anddf = pd.read_excel(andpath)
            condition = (anddf['Экзамен'] == f'{exam}') & (anddf['Время'] == f'{time}')
            anddf = anddf.drop(anddf[condition].index)
            anddf.to_excel(andpath, index=False)
        except FileNotFoundError:
            return

    if (action == 'removeall_queues'):
        path = os.path.join(os.path.dirname(sys.argv[0]), 'db_groups')
        andpath = os.path.join(os.path.dirname(sys.argv[0]), 'final_record')
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            os.unlink(file_path)
        for filename in os.listdir(andpath):
            file_path = os.path.join(andpath, filename)
            os.unlink(file_path)
            
def clean_alldata():
    path = os.path.join(os.path.dirname(sys.argv[0]), 'final_record')
    for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            try:
                os.unlink(file_path)
            except Exception as e:
                print(f"Не удалось удалить {file_path}. Причина: {e}")
                
def add_queue_group(groupex_andtime):
    path = os.path.join(os.path.dirname(sys.argv[0]), 'db_groups', f'{groupex_andtime[0]}db.xlsx')
    groupex_andtime = groupex_andtime[:3]
    if(len(groupex_andtime)==3):
        try:
            df = pd.read_excel(path)
            new_row = {'Экзамен': f'{groupex_andtime[1]}', 'Время': f'{groupex_andtime[2]}'}
            df.loc[len(df)] = new_row
            df.drop_duplicates(keep='last', inplace=True)
            df.to_excel(path, index=False)

        except FileNotFoundError:
            columns = ['Экзамен', 'Время']
            df = pd.DataFrame(columns=columns)
            df.to_excel(path, index=False)
            add_queue_group(groupex_andtime)

    else:
        return
    
def contains_digits(s):
    return bool(re.search(r'\d', s))