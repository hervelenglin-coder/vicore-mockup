import pandas as pd
from sqlalchemy_config import db_session, spring_location, train_pass

path_list = [
    ".//static//1M00-20240206154354//best_camera_result.csv",
    ".//static//2K18-20240206162448//best_camera_result.csv",
    ".//static//9N57-20240206164929//best_camera_result.csv",
    ".//static//1M00_2-20240206154354//best_camera_result.csv",
    ".//static//2K18_2-20240206162448//best_camera_result.csv",
    ".//static//9N57_2-20240206164929//best_camera_result.csv",
]


train_number = len(path_list)
all_system_id = [1 if i < train_number / 2 else 2 for i in range(train_number)]
all_system_name = ["System_1" if i < train_number / 2 else "System_2" for i in range(train_number)]

all_train_service_code = ["1M00", "2K18", "9N57", "1M00_2", "2K18_2", "9N57_2"]
all_train_id = ["154354", "162448", "164929", "154354_2", "162448_2", "164929_2"]

for i in range(train_number):
    data = pd.read_csv(path_list[i])
    data_length = len(data)
    # train_pass
    time_start = data["Trigger_time"].tolist()[0]
    time_finished = data["Trigger_time"].tolist()[-1]
    train_id = all_train_id[i]
    train_service_code = all_train_service_code[i]
    system_id = all_system_id[i]
    system_name = all_system_name[i]

    # spring_location
    train_pass_id = []
    train_pass_id.extend([i + 1] * data_length)
    carriage_number = [(i // 16) + 1 for i in range(data_length)]
    wheel_number = [(i % 8) + 1 for i in range(data_length)]
    side = [False if i % 2 == 0 else True for i in range(data_length)]
    confidence = data["confidence"].round(2).tolist()
    timestamp = data["Trigger_time"].tolist()
    best_image_path = data["File_name"].tolist()

    with db_session() as session:
        new_train_pass = train_pass(
            time_start=time_start,
            time_finished=time_finished,
            train_id=train_id,
            train_service_code=train_service_code,
            system_id=system_id,
            system_name=system_name,
        )
        session.add(new_train_pass)
        session.commit()

    for j in range(data_length):
        with db_session() as session:
            new_spring_location = spring_location(
                train_pass_id=train_pass_id[j],
                carriage_number=carriage_number[j],
                wheel_number=wheel_number[j],
                side=side[j],
                confidence=confidence[j],
                best_image_path=best_image_path[j],
                timestamp=timestamp[j],
            )
            session.add(new_spring_location)
            session.commit()
