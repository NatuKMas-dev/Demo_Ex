DROP TABLE IF EXISTS notes;
DROP TABLE IF EXISTS users;
CREATE TABLE users (
id INTEGER PRIMARY KEY,
login TEXT NOT NULL UNIQUE
);
CREATE TABLE notes (
id INTEGER PRIMARY KEY,
title TEXT NOT NULL,
content TEXT,
id_user INTEGER NOT NULL REFERENCES users(id),
created_at TEXT
);
INSERT INTO users (id, login) VALUES
(1, 'admin'),
(2, 'user25'),
(3, 'ivanov'),
(4, 'petrova');
INSERT INTO notes (id, title, content, id_user, created_at) VALUES
(1, 'Конференция ИТ', 'Содержимое заметки', 2,
'03.02.2027'),
(2, 'Список задач', 'Купить продукты, позвонить в банк', 1,
'07.02.2027'),
(3, 'Отчёт за квартал', 'Подготовить отчёт для руководителя', 3,
'14.02.2027'),
(4, 'Идеи для проекта', 'Добавить авторизацию и кэширование', 2,
'21.02.2027'),
(5, 'Встреча с командой', 'Обсудить сроки и распределение задач', 4,
'28.02.2027');