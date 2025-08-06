import json

class UsersListView:
    def __init__(self, users, path):
        self.users = users
        self.path = path
    
    def export(self):
        formated_results = []
        for user in self.users:
            user_dict = self.format_user(user)
            if isinstance(user_dict["shirt_size"], set):
                user_dict["shirt_sizes"] = list(user_dict["shirt_sizes"])
    
            formated_results.append()

        with open(self.path, "w") as f:
            try:
                json.dump(formated_results, f, indent=4)
            except json.JSONDecodeError as e:
                print(e)

    def format_user(self, user):
        return {
                "name": user["first_name"] + user["last_name"],
                "experience": float(user["years_of_experience"]),
                "salary": user["annual_salary"],
        }

class UsersListViewAPI(UsersListView):
    # violates LP
    def format_user(self, user):
        return {
            "name": user["first_name"],
            "shirt_size": {user["shirt_size"], "S"},
        } 

export_view = UsersListViewAPI(
    [
        {
          "id": 1,
          "first_name": "Ezequiel",
          "last_name": "Jiri",
          "age": 28,
          "job_title": "Research Nurse",
          "email": "ejiri0@constantcontact.com",
          "gender": "Bigender",
          "shirt_size": "XL",
          "favorite_color": "#fa173b",
          "iso_code": "PH",
          "years_of_experience": 10,
          "annual_salary": 184958.79
        },
        {
          "id": 2,
          "first_name": "Kara",
          "last_name": "Benkin",
          "age": 63,
          "job_title": "Junior Executive",
          "email": "kbenkin1@toplist.cz",
          "gender": "Genderfluid",
          "shirt_size": "XL",
          "favorite_color": "#9b8185",
          "iso_code": "YE",
          "years_of_experience": 4,
          "annual_salary": 197442.13
        },
    ], 
    path="export.json")

export_view.format_user()