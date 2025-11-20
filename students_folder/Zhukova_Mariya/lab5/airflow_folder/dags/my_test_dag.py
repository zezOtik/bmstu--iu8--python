from airflow import DAG # по умолчанию шедулер читает только файлики с таким началом, даже если эта строка будет закомменчена

from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator

from datetime import datetime

with DAG(dag_id='my_test_dag', # то, что отображается как название дага в ui - щас появится даг, а в нем нужно завести задачки
         schedule_interval='0 7 * * *', # крон исполнение (время), шедулер выполняет только в конец интервала (т.е. если запустили 11, он выполнит 12го числа)
         max_active_runs=1, # количество выполнений (тут 1 раз)
         start_date = datetime(2025,11,19), # ну важный атрибут, без него будет кидать ошибки
         catchup=False) as dag: # отвечает за подсчет дней (механизм backin?) (будет выполнять до даты)
    
    task1 = EmptyOperator(task_id = 'test_task_my')

    # task2 = EmptyOperator(task_id = 'test_task_my_2')

    # task3 = EmptyOperator(task_id = 'test_task_my_3')

    # run = task1 >> task2 # 2 после 1 выполняется, связь между дагами типо 
    # тут типо task2 зависит от task1
    # если вот так - task1 << task2 - то они будут идти в обратном порядке 
    #run = task1 >> [task2,task3] # параллельное соединение дагов!

    # если делать цикл - ошибка (task1 >> [task2,task3] >> task1) - airflow не любит циклы
    # связь многие ко многим - airflow не любит:
        #   run = task_1 >> [ task_2, task_3 ] >>  [ task_4, task_5] - ошибка, не саппортит
        #   run = task_1 >> [ task_2, task_3 ] >> task_dummy >> [ task_4, task_5] - вот это уже саппортит (вот тут и нужны пустые операторы, просто как связки в этой ситуации)

    

        # важно чтобы task_id в рамках 1 дага были уникальны, иначе ошибка
            
        # Таски = операторы, операторы что-то делают
        # Emptyoperator - ниче не делает, нужен как заглушка
        # по дефолту он раз в 30 секунд парсит даг директорию в ui из этой папки, поэтому достаточно просто сюда даг добавить и он будет в ui через 30сек
        # шедулер парсит питонячьи файлики

        # downsteram и upstream - те же связи между дагами
        #first_task.set_downstream(second_task) -  2 таск запустится после 1
        #first_task.set_upstream(second_task) -  1 таск запустится после 2

        # динамическая даг генерация - в рамках 1 питон файла создается куча дагов, поднимается и 
        # менеджерится, еще есть динамическая таск генерация, крч на практике часте исп set upstream и downstream 

        # Смотри на  Баш оператор
    t5 = BashOperator(task_id = 'test_task_my_5',
                       bash_command = "echo Hello_world  {{ds}}",
                       dag=dag) 
    
    task1.set_downstream(t5)
