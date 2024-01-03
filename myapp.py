# импорт необходимых модулей
from collections import Counter
from datetime import datetime
from flask import Flask, redirect, url_for
from flask import render_template
from flask import request
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

# у меня начинал ложиться сайт, как только я стала рендерить изображения в
# своем коде, подсказка из документации помогла мне пофиксить эту проблему
# https://matplotlib.org/stable/users/explain/figure/backends.html
# это значит что я рендерю png, растерную high-quality графику
matplotlib.use("Agg")

app = Flask(__name__)


# функция для сбора данных анкеты
@app.route("/data_collection")
def update_data():
    # открываем файл, где мы храним все данные на дозапись
    with open("/home/fromdeath2morning/FlaskPrototypesApp/data.csv", "a") as file:
        # сбор данных
        new_data = [
            request.args["age"],
            request.args["season"],
            request.args["planet"],
            request.args["tomatoes"],
            request.args["fruits"].lower().strip(),
            request.args["vegetables"].lower().strip(),
            request.args["nuts"].lower().strip(),
            request.args["berries"].lower().strip(),
            request.args["birds"].lower().strip(),
            request.args["plants"].lower().strip(),
        ]
        # если пользователь не заполнил какие-то поля, то заменяем пустоту
        # на None, чтобы потом с ней работать в dataframe
        # отдельно обрабатываем возраст и заменяем его на 0, чтобы
        # потом можно было считать числовое среднее значение
        if new_data[0] == "":
            new_data[0] = "0"
        for i in range(1, len(new_data)):
            if new_data[i] == "":
                new_data[i] = "None"
        # записываем все собранные данные в файл
        file.write(f'{",".join(new_data)}\n')

    # после сбора данных рендерим страницу с благодарностью за заполнение
    # анкеты
    return render_template("gratitude_form.html")


# рендер главной страницы
@app.route("/")
def main():
    return render_template("main.html")


# рендер страницы с анкетой
@app.route("/form")
def form():
    return render_template("form.html")


# рендер страницы со статистикой
@app.route("/stats")
def stats():
    df = pd.read_csv("/home/fromdeath2morning/FlaskPrototypesApp/data.csv")

    # идея с redirect на страницу анкеты, если не собрано никаких данных
    # взята отсюда https://github.com/hse-ling-python/seminars/blob/master/flask_applications/flask_2.ipynb
    if df.shape[0] < 1:
        return redirect(url_for("form"))

    # общее количество заполненных анкет
    amount_of_people = df.shape[0]

    # средний возраст заполнивших анкету
    mean_age = df["age"].mean()

    # количество любителей помидоров
    tomatoes_cnt = float(Counter(df["tomatoes"])["Да"])

    # самое популярное время года
    favourite_season = df["season"].value_counts().idxmax()

    # самая популярная планета
    favourite_planet = df["planet"].value_counts().idxmax()

    # cбор статистики по количеству уникальных объектов, которые встретились
    # среди данных
    unique_fruits = len(df["fruits"].value_counts())
    unique_vegetables = len(df["vegetables"].value_counts())
    unique_nuts = len(df["nuts"].value_counts())
    unique_berries = len(df["berries"].value_counts())
    unique_birds = len(df["birds"].value_counts())
    unique_plants = len(df["plants"].value_counts())

    # помещаем данные в список
    unique_elements = [
        unique_fruits,
        unique_vegetables,
        unique_nuts,
        unique_berries,
        unique_birds,
        unique_plants,
    ]

    # помещаем статистические данные в список, чтобы затем передать
    # в качестве аргумента при рендере страницы
    content = [
        amount_of_people,
        mean_age,
        tomatoes_cnt,
        favourite_season,
        favourite_planet,
        unique_elements,
    ]

    # как менять цвета или добавлять процентны на график в pie-chart было взято
    # отсюда https://matplotlib.org/stable/gallery/pie_and_polar_charts/pie_features.html

    # генерация графиков по каждому прототипу
    for prototype in ["fruits", "vegetables", "nuts", "berries", "birds", "plants"]:
        # берем топ-5 по количеству голосов
        labels = list(df[prototype].value_counts().head(5).to_dict().keys())
        sizes = list(df[prototype].value_counts().head(5).to_dict().values())

        # создаем график
        plt.pie(
            sizes,
            labels=labels,
            colors=["#d896ff", "#efbbff", "#e5d0ff", "#dabcff", "#cca3ff"],
            autopct="%1.1f%%",
        )

        # сохраняем график в директорию static
        plt.savefig(f"/home/fromdeath2morning/FlaskPrototypesApp/static/pie_{prototype}.png", dpi=300)

        # закрытие необходимо для того, чтобы последующие графики
        # генерировались не в том же "окне"
        # подробнее -- здесь https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.close.html
        plt.close()

    # рендер страницы со статистикой
    return render_template("stats.html", content=content)


# рендер страницы для сбора отзывов о сайте
@app.route("/feedback")
def feedback():
    return render_template("feedback.html")


# функция для сбора отзывов
@app.route("/feedback_collection")
def feedback_collection():
    # открываем файл с отзывами на дозапись
    with open("/home/fromdeath2morning/FlaskPrototypesApp/feedback.txt", "a") as file:
        # записываем сам отзыв + по приколу время, в которое он был отправлен
        file.write(f"{datetime.now()}\t{request.args['Feedback']}\n")

    # после сбора отзывов рендерим страницу с благодарностью за отзыв
    return render_template("gratitude_feedback.html")


if __name__ == "__main__":
    app.run()
