# -*- coding: utf-8 -*-

# Commented out IPython magic to ensure Python compatibility.
import numpy as np #для матричных вычислений
import pandas as pd #для анализа и предобработки данных
import matplotlib.pyplot as plt #для визуализации
import seaborn as sns #для визуализации

from sklearn import linear_model #линейные модели
from sklearn import metrics #метрики
from sklearn import ensemble

from sklearn.datasets import load_diabetes
from sklearn.ensemble import StackingRegressor
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.metrics import classification_report

import warnings # для игнорирования предупреждений
#Игнорируем варнинги
warnings.filterwarnings('ignore')

# Устанавливаем стиль визуализаций в matplotlib
# %matplotlib inline
plt.style.use('seaborn')

from google.colab import drive
drive.mount('/content/drive')

# Устанавливаем максимальное количество отображаемых столбцов
pd.set_option('display.max_columns', None)

# Настраиваем ширину вывода
pd.set_option('display.width', 1000)

# Загружаем данные
train = pd.read_csv('/content/train.csv', sep=',')
test = pd.read_csv('/content/test.csv')

# Посмотрим на данные
print(train.head())
print(train.info())

"""*   PassengerId: Идентификатор пассажира.
*   Survived: Целевая переменная (0 — не выжил, 1 — выжил).
*   Pclass: Класс пассажирского билета (1 — первый, 2 — второй, 3 — третий).
*   Name: Имя пассажира.
*   Sex: Пол.
*   Age: Возраст.
*   SibSp: Количество братьев, сестер, супругов на борту.
*   Parch: Количество родителей, детей на борту.
*   Ticket: Номер билета.
*   Fare: Стоимость билета.
*   Cabin: Номер каюты.
*   Embarked: Порт посадки (C — Cherbourg, Q — Queenstown, S — Southampton).

Также видим, что в признаках Age, Cabin и Embarked есть пропущенные значения.
Необходимо будет обработать эти пропуски на этапе предобработки данных.

Начнём с анализа взаимосвязей между выживаемостью и признаками. Перед этим важно рассчитать корреляцию между признаками, чтобы увидеть, какие признаки могут оказывать влияние на результат.
"""

# Преобразуем пол в числовое значение: male = 0, female = 1
train['Sex'] = train['Sex'].map({'male': 0, 'female': 1})

# Удалим нечисловые столбцы, такие как 'Name' и 'Ticket'
numeric_features = train.select_dtypes(include=['int64', 'float64'])

# Вычисляем корреляцию числовых признаков
corr_matrix = numeric_features.corr()

# Выводим корреляцию с целевой переменной (Survived)
print(corr_matrix['Survived'].sort_values(ascending=False))

"""Результаты корреляционного анализа показывают, как каждый числовой признак связан с целевой переменной **Survived**. Корреляция измеряется в диапазоне от -1 до 1, где:

- **1** означает полную положительную корреляцию (признак и целевая переменная возрастают вместе),
- **-1** означает полную отрицательную корреляцию (признак и целевая переменная изменяются в противоположных направлениях),
- **0** означает отсутствие корреляции.

Теперь разберем выводы для каждого признака:

1. **Fare (0.257)**: Этот признак имеет положительную корреляцию с выживаемостью. Это означает, что более высокие цены на билеты в среднем ассоциируются с большей вероятностью выживания. Но этот признак также может относиться к классу пассажира.

2. **Parch (0.081)**: Положительная, но слабая корреляция между количеством родителей/детей на борту и выживаемостью. Это может означать, что пассажиры с семьями имели немного более высокие шансы выжить, но этот эффект незначителен.

3. **PassengerId (-0.005)**: Практически нулевая корреляция, что логично, так как этот признак просто уникальный идентификатор и не связан с выживаемостью.

4. **SibSp (-0.035)**: Отрицательная, но очень слабая корреляция между количеством братьев/сестер/супругов на борту и выживаемостью. Это означает, что наличие этих родственников на борту незначительно снижало шансы на выживание.

5. **Age (-0.077)**: Возраст имеет отрицательную корреляцию с выживаемостью. Это значит, что с увеличением возраста вероятность выживания немного снижалась. Возможно, более молодые пассажиры имели больше шансов выжить.

6. **Pclass (-0.338)**: Сильная отрицательная корреляция с выживаемостью. Это означает, что пассажиры из более низких классов (например, 3-й класс) имели гораздо меньшие шансы выжить по сравнению с пассажирами более высоких классов (например, 1-й класс).

7. **Sex (0.54)**: Имеет одну из самых сильных корреляций с выживаемостью, так как женщины выживали чаще, чем мужчины.

### Общие выводы:

- **Pclass**, **Fare** и **Sex** — три наиболее значимых признака для предсказания выживаемости. Высокий класс и высокая стоимость билета связаны с большей вероятностью выжить.
- Признаки **Parch** и **SibSp**, связанные с количеством членов семьи на борту, имеют слабую связь с выживаемостью.
- **Age** также оказывает слабое, но заметное влияние: чем старше пассажир, тем ниже его шансы выжить.

Исследуем данные, чтобы понять распределение целевой переменной и взаимосвязи между признаками.
"""

# Распределение выживших и невыживших
sns.countplot(x='Survived', data=train)
plt.title('Распределение выживших и погибших')
plt.xlabel('Выжил (1) или нет (0)')
plt.ylabel('Количество пассажиров')
plt.show()

# Взаимосвязь пола и выживаемости
sns.countplot(x='Survived', hue='Sex', data=train)
plt.title('Выживаемость в зависимости от пола')
plt.xlabel('Выжил (1) или нет (0)')
plt.ylabel('Количество пассажиров')
plt.legend(title='Пол', loc='upper right')
plt.show()

"""График показывает, что:
*   Большинство выживших — женщины.
*   Большинство мужчин не выжили.
"""

# Взаимосвязь класса и выживаемости
sns.countplot(x='Survived', hue='Pclass', data=train)
plt.title('Выживаемость в зависимости от класса')
plt.xlabel('Выжил (1) или нет (0)')
plt.ylabel('Количество пассажиров')
plt.legend(title='Класс', loc='upper right')
plt.show()

"""*   Пассажиры первого класса выживали чаще.
*   Из пассажиров второго класса выжила почти половина.
*   Количество выживших пассажиров из третьего класса меньше всего.
"""

# Распределение возраста
plt.figure(figsize=(10, 6))
sns.histplot(train['Age'].dropna(), bins=30)
plt.title('Распределение возраста пассажиров')
plt.xlabel('Возраст')
plt.ylabel('Количество пассажиров')
plt.show()

"""Из графика видно, что данные распределены практически нормально, однако есть пропущенные значения, которые необходимо обработать."""

# Количество пропущенных значений по столбцам
print(train.isnull().sum())

"""Видно, что в признаке Age 177 пропусков, в Cabin содержится больше всего пропусков (687 из 891), и в Embarked всего 2 пропуска.

Чтобы избежать потери данных, предлагаю заменить пропуски в признаке Age медианными значениями, а в признаке Embarked - модой, так как их там всего 2. Признак Cabin имеет слишком много пропусков (более 70% в данных о пассажирах Титаника), поэтому просто удалять строки или признак — не лучший вариант. Вместо этого можно использовать кластеризация по первым буквам Cabin: Если оставшихся данных о каютах достаточно, можно использовать первые буквы кают (например, A, B, C) для создания новой категории. Это может дать информацию о расположении пассажиров на корабле, что может быть полезно. Пусть U будет означать 'Unknown' - неизввестную каюту.
"""

# Заполним пропуски в возрасте медианным значением
train['Age'].fillna(train['Age'].median(), inplace=True)

# Заполним пропуски в Embarked самым частым значением
train['Embarked'].fillna(train['Embarked'].mode()[0], inplace=True)

# Преобразуем Cabin, извлекая первую букву
train['Cabin'] = train['Cabin'].apply(lambda x: x[0] if pd.notnull(x) else 'U')

# Посмотрим на dataset после преобразования
print(train.head())

"""Для улучшения модели можно также попробовать создать новые признаки или преобразовать уже существующие. Например, признак "Family_Size" — семейное положение, которое объединяет количество братьев/сестер/супругов (SibSp) и родителей/детей (Parch).Этот признак может быть полезен для предсказания, поскольку наличие семьи на борту могло повлиять на вероятность выживания.
Признак "Is_Alone" — один ли пассажир путешествовал.
"""

train['Family_Size'] = train['SibSp'] + train['Parch'] + 1
train['Is_Alone'] = 1  # По умолчанию, пассажир один
train['Is_Alone'].loc[train['Family_Size'] > 1] = 0  # Пассажир не один, если есть семья

"""Также нужно преобразовать категориальные признаки, такие как Embarked, чтобы они были закодированы числовым способом, понятным для моделей.

Embarked (порт посадки): Преобразуем его в бинарные признаки с помощью One-Hot Encoding. Этот метод преобразует каждую категорию в отдельную колонку с значениями 0 и 1. Используем drop_first=True, чтобы избежать коллинеарности (избыточности данных).
"""

train = pd.get_dummies(train, columns=['Embarked'], drop_first=True)

train = pd.get_dummies(train, columns=['Pclass'], drop_first=True)

"""Некоторые модели чувствительны к масштабу данных (например, логистическая регрессия и SVM). Для таких моделей полезно стандартизировать числовые признаки, такие как Age и Fare."""

from sklearn.preprocessing import StandardScaler

# Масштабируем только числовые признаки
scaler = StandardScaler()
train[['Age', 'Fare']] = scaler.fit_transform(train[['Age', 'Fare']])

print(train.head())

"""Теперь, когда были обработаны все данные, стоит рассмотреть отбор признаков для обучения модели. На основе корреляции с целевой переменной и важности признаков можно выбрать наиболее значимые для обучения.

Основные признаки, которые стоит использовать:
1. Sex (пол),
2. Pclass (класс билета),
3. Age (возраст),
4. Fare (стоимость билета),
5. Family_Size (размер семьи),
6. Is_Alone (один ли пассажир),
7. Embarked (порт посадки).
"""

# Выбираем важные признаки для модели
features = ['Sex', 'Age', 'Fare', 'Family_Size', 'Is_Alone', 'Pclass_2', 'Pclass_3', 'Embarked_Q', 'Embarked_S']
X = train[features]
y = train['Survived']

#Теперь стоит разделить данные на обучающую и тестовую выборки
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

"""Используем кросс-валидацию K-fold для оценки модели."""

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import classification_report

# Создаем модель логистической регрессии
logreg_model = LogisticRegression(max_iter=200, random_state=42)

# Получаем предсказания с помощью кросс-валидации
y_pred = cross_val_predict(logreg_model, X, y, cv=5)

# Выводим отчет о классификации, включая точность, полноту и F1-score для каждого класса
print("Отчет о классификации для логистической регрессии:")
print(classification_report(y, y_pred))

# Если нужно также вывести метрики кросс-валидации по accuracy
from sklearn.model_selection import cross_val_score

# Оцениваем accuracy модель с помощью кросс-валидации
logreg_cv_scores = cross_val_score(logreg_model, X, y, cv=5, scoring='accuracy')

# Выводим среднюю точность
print(f'Средняя точность (Accuracy): {logreg_cv_scores.mean():.4f}')

"""В результате можно увидеть:

1. **Accuracy (точность):** 79.9% — модель правильно предсказала исход (выживание или гибель) примерно в 80% случаев. Это хорошая базовая точность для задачи, но есть место для улучшений.

2. **Precision (точность предсказаний):**
   - Для класса **0** (не выжил) — 0.82. Это значит, что среди всех пассажиров, которых модель предсказала как "не выживших", 82% действительно не выжили.
   - Для класса **1** (выжил) — 0.77. Среди тех, кого модель предсказала как "выживших", 77% действительно выжили.

3. **Recall (полнота):**
   - Для класса **0** — 0.87. Модель нашла 87% всех реальных "не выживших".
   - Для класса **1** — 0.69. Модель правильно определила 69% всех реальных "выживших", то есть пропустила примерно 31% тех, кто на самом деле выжил.

4. **F1-Score:** это среднее между precision и recall. Для класса **0** — 0.84, для класса **1** — 0.72. Это показывает, что модель лучше справляется с предсказанием "не выживших", чем с предсказанием "выживших".

**Вывод:**
Модель логистической регрессии показывает неплохую точность (около 80%), но ее способность находить всех "выживших" пассажиров (recall для класса 1) могла бы быть выше. Это может быть признаком того, что модель склонна предсказывать больше "не выживших".

После логистической регрессии стоит попробовать другие модели, такие как RandomForest и GradientBoosting, чтобы посмотреть, как они справляются с задачей.
"""

from sklearn.ensemble import RandomForestClassifier

# Создаем модель случайного леса
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)

# Получаем предсказания с помощью кросс-валидации
y_pred_rf = cross_val_predict(rf_model, X, y, cv=5)

# Выводим отчет о классификации, включая точность, полноту и F1-score для каждого класса
print("Отчет о классификации для случайного леса:")
print(classification_report(y, y_pred_rf))

# Если нужно также вывести метрики кросс-валидации по accuracy
from sklearn.model_selection import cross_val_score

# Оцениваем accuracy модель с помощью кросс-валидации
rf_cv_scores = cross_val_score(rf_model, X, y, cv=5, scoring='accuracy')

# Выводим среднюю точность
print(f'Средняя точность (Accuracy) для случайного леса: {rf_cv_scores.mean():.4f}')

"""Случайный лес показывает более высокую точность по сравнению с логистической регрессией (80% против 79.9%) и лучше сбалансирован между precision и recall для обоих классов. Однако recall для класса "выжившие" (1) все еще может быть улучшен, так как 25% выживших остаются непризнанными моделью.

На основе предыдущих результатов, можно попробовать несколько методов для улучшения модели. Один из лучших вариантов — это настройка гиперпараметров с помощью GridSearchCV. Этот метод позволяет найти наилучшие настройки для модели случайного леса.
"""

from sklearn.model_selection import GridSearchCV

# Определяем параметры для настройки
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 10, 20, 30],
    'min_samples_split': [2, 5, 10],
}

# Создаем объект GridSearchCV
grid_search = GridSearchCV(estimator=RandomForestClassifier(random_state=42),
                           param_grid=param_grid,
                           cv=5,
                           scoring='accuracy',
                           n_jobs=-1)

# Обучаем модель с настройкой гиперпараметров
grid_search.fit(X, y)

# Лучшие параметры и результат
best_rf_model = grid_search.best_estimator_
best_score = grid_search.best_score_

print(f'Лучшие параметры: {grid_search.best_params_}')
print(f'Лучший результат точности: {best_score:.4f}')

# Результаты кросс-валидации
print("Результаты до улучшения:")
print(f'Логистическая регрессия: {logreg_cv_scores.mean():.4f}')
print(f'Случайный лес: {rf_cv_scores.mean():.4f}')

# Оценим новую модель случайного леса с лучшими параметрами
new_rf_cv_scores = cross_val_score(best_rf_model, X, y, cv=5, scoring='accuracy')
print(f'Случайный лес после настройки гиперпараметров: {new_rf_cv_scores.mean():.4f}')

"""Настройка гиперпараметров с использованием GridSearchCV помогла значительно улучшить качество модели случайного леса, увеличив точность с 0.8025 до 0.8328. Это показывает, что правильный подбор гиперпараметров может существенно улучшить производительность модели. Однако я хочу попробовать еще улучшить данную модель с помощью градиентного бустинга."""

from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import GradientBoostingClassifier

# Определяем гиперпараметры для настройки
param_grid = {
    'n_estimators': [100, 200, 300],      # Количество деревьев
    'learning_rate': [0.01, 0.05, 0.1],  # Шаг обновления модели
    'max_depth': [3, 4, 5],              # Глубина деревьев
    'subsample': [0.8, 1.0],             # Доля данных, используемая для построения деревьев
}

# Создаем модель градиентного бустинга
gbc = GradientBoostingClassifier(random_state=42)

# Настраиваем модель с помощью GridSearchCV
grid_search = GridSearchCV(gbc, param_grid, cv=5, scoring='accuracy', n_jobs=-1)
grid_search.fit(X, y)

# Выводим лучшие параметры и точность
print(f'Лучшие параметры: {grid_search.best_params_}')
print(f'Лучшая точность: {grid_search.best_score_:.4f}')

"""Результаты показывают, что после настройки гиперпараметров точность модели увеличилась до 0.8418, что значительно лучше, чем показатели у логистической регрессии (0.7991) и случайного леса до (0.8025) и после настройки (0.8328).

Таким образом, модель градиентного бустинга с оптимизированными параметрами показала наилучшую точность из всех рассмотренных моделей на текущий момент.

Теперь можно перейти непосредственно к предсказаниям для файла test.csv

"""

test = pd.read_csv('/content/test.csv')

# Функция предобработки данных
def preprocess_data(data):
    # Преобразуем пол в числовое значение
    data['Sex'] = data['Sex'].map({'male': 0, 'female': 1})

    # Заполняем пропуски
    data['Age'].fillna(data['Age'].median(), inplace=True)
    data['Fare'].fillna(data['Fare'].median(), inplace=True)
    data['Embarked'].fillna(data['Embarked'].mode()[0], inplace=True)

    # Создаем новые признаки
    data['Family_Size'] = data['SibSp'] + data['Parch'] + 1
    data['Is_Alone'] = 1
    data['Is_Alone'].loc[data['Family_Size'] > 1] = 0

    # Кодируем категориальные признаки
    data = pd.get_dummies(data, columns=['Embarked'], drop_first=True)
    data = pd.get_dummies(data, columns=['Pclass'], drop_first=True)

    return data

test = preprocess_data(test)

# Масштабируем числовые признаки
scaler = StandardScaler()
train[['Age', 'Fare']] = scaler.fit_transform(train[['Age', 'Fare']])
test[['Age', 'Fare']] = scaler.transform(test[['Age', 'Fare']])

# Предсказания на тестовом наборе
X_test_final = test[features]
y_test_pred = grid_search.predict(X_test_final)

# Создание DataFrame для сохранения результатов
results = pd.DataFrame({
    'PassengerId': test['PassengerId'],
    'Survived': y_test_pred
})

# Сохранение результатов в CSV файл для загрузки на Kaggle
results.to_csv('submission.csv', index=False, header=True)
from google.colab import files
files.download('submission.csv')

# Итоги
total_survived = results['Survived'].sum()
total_not_survived = len(results) - total_survived
print(f"Количество выживших: {total_survived}")
print(f"Количество погибших: {total_not_survived}")

print(results.head())
print(results.info())
print(results.shape)

"""В процессе работы были выполнены следующие шаги:
1. **Предобработка данных**:
   - Данные были предварительно обработаны, что включало:
     - Преобразование категориальных признаков в числовые (например, пол).
     - Заполнение пропущенных значений для признаков `Age`, `Fare` и `Embarked`.
     - Создание новых признаков, таких как `Family_Size` и `Is_Alone`, для увеличения информативности модели.
     - Кодирование категориальных переменных с помощью one-hot encoding.

2. **Модель и обучение**:
   - В процессе работы были протестированы несколько моделей, включая логистическую регрессию и случайный лес.Однако лучшую производительность показал градиентный бустинг (Gradient Boosting Classifier).
   - Проведена настройка гиперпараметров модели с использованием **GridSearchCV**, что позволило выявить наилучшие параметры для достижения максимальной точности.
   - Обучение модели проводилось на подготовленных данных с использованием кросс-валидации, что позволяет лучше оценить устойчивость модели к переобучению.

3. **Предсказания и результаты**:
   - На тестовом наборе данных модель предсказала количество выживших пассажиров, что дало общее количество выживших около **217** и погибших **201**.
   - Эти результаты кажутся высокими и могут потребовать дополнительного анализа, чтобы понять, соответствует ли такая высокая выживаемость реальным данным.

### Заключение
В результате работы была разработана и обучена модель для предсказания выживаемости пассажиров Титаника с высокой точностью. Полученные результаты показывают потенциал использованных методов, однако дальнейший анализ и тестирование на новых данных помогут повысить надежность модели и её практическую применимость.
"""