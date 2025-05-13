import tkinter as tk
from tkinter import ttk, messagebox # Keep messagebox for critical errors only
import secrets # For cryptographically strong random numbers
import json
import os

class MealPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weekly Meal Planner")
        self.root.geometry("800x600") # Adjusted size for new entry field
        self.root.configure(bg="#f0f0f0")

        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.style.configure("TLabel", background="#f0f0f0", font=("Arial", 11))
        self.style.configure("Header.TLabel", background="#f0f0f0", font=("Arial", 14, "bold"))
        self.style.configure("TButton", font=("Arial", 10, "bold"), padding=6)
        self.style.map("TButton",
                         foreground=[('active', 'green'), ('!disabled', 'black')],
                         background=[('active', '#e0e0e0')])
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("Red.TButton", foreground="white", background="#c0392b")
        self.style.map("Red.TButton", background=[('active', '#a93226')])
        self.style.configure("TEntry", font=("Arial", 10), padding=3)

        self.meals_file = "meals_data.json"
        self.all_meals = self.load_meals()
        self.weekly_plan = [""] * 7 # Monday to Sunday

        self.days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.meal_labels = {} # To store the meal label widgets for each day

        self.setup_ui()
        self.update_available_meals_display()
        self.update_weekly_plan_display()

    def load_meals(self):
        if os.path.exists(self.meals_file):
            try:
                with open(self.meals_file, 'r') as f:
                    meals = json.load(f)
                    return sorted(list(set(m for m in meals if m and m.strip())))
            except json.JSONDecodeError:
                messagebox.showerror("Load Error", f"Could not read {self.meals_file}. It might be corrupted. Starting with an empty list.")
                return []
            except Exception as e:
                messagebox.showerror("Load Error", f"An unexpected error occurred while loading meals: {e}")
                return []
        return []

    def save_meals(self):
        try:
            with open(self.meals_file, 'w') as f:
                json.dump(sorted(list(set(self.all_meals))), f, indent=4)
        except IOError:
            messagebox.showerror("Save Error", f"Could not save meals to {self.meals_file}.")
        except Exception as e:
            messagebox.showerror("Save Error", f"An unexpected error occurred while saving meals: {e}")


    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10 10 10 10")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Left Frame for Available Meals & Adding New Meals
        left_frame = ttk.Frame(main_frame, padding="10 10 10 10", relief="groove", borderwidth=2)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        ttk.Label(left_frame, text="Available Meals", style="Header.TLabel").pack(pady=(0, 10))

        self.available_meals_listbox = tk.Listbox(left_frame, height=12, font=("Arial", 10), selectbackground="#a6a6a6", activestyle="none", exportselection=False)
        self.available_meals_listbox.pack(fill=tk.BOTH, expand=True, pady=(0,10))
        scrollbar = ttk.Scrollbar(self.available_meals_listbox, orient=tk.VERTICAL, command=self.available_meals_listbox.yview)
        self.available_meals_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        delete_meal_button = ttk.Button(left_frame, text="Delete Selected Meal", command=self.delete_selected_meal)
        delete_meal_button.pack(fill=tk.X, pady=(5,10))

        ttk.Label(left_frame, text="Add New Meal:", font=("Arial", 11, "bold")).pack(pady=(10,2), anchor="w")
        self.new_meal_entry = ttk.Entry(left_frame, font=("Arial", 10), width=30)
        self.new_meal_entry.pack(fill=tk.X, pady=(0,5))
        self.new_meal_entry.bind("<Return>", self.add_meal_from_entry) # Allow adding with Enter key

        add_meal_button = ttk.Button(left_frame, text="Add Meal to List", command=self.add_meal_from_entry)
        add_meal_button.pack(fill=tk.X)


        # Right Frame for Weekly Plan
        right_frame = ttk.Frame(main_frame, padding="10 10 10 10", relief="groove", borderwidth=2)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        ttk.Label(right_frame, text="This Week's Meal Plan", style="Header.TLabel").pack(pady=(0, 15))

        plan_grid_frame = ttk.Frame(right_frame)
        plan_grid_frame.pack(fill=tk.X)

        for i, day in enumerate(self.days_of_week):
            day_label = ttk.Label(plan_grid_frame, text=f"{day}:", font=("Arial", 11, "bold"))
            day_label.grid(row=i, column=0, sticky="w", pady=3, padx=5)
            meal_label = ttk.Label(plan_grid_frame, text="", width=30, anchor="w", relief="sunken", padding=3, font=("Arial", 10))
            meal_label.grid(row=i, column=1, sticky="ew", pady=3, padx=5)
            reroll_button = ttk.Button(plan_grid_frame, text="Re-roll", command=lambda d=day: self.reroll_meal(d), width=8)
            reroll_button.grid(row=i, column=2, sticky="e", padx=5)
            self.meal_labels[day] = meal_label

        plan_grid_frame.columnconfigure(1, weight=1)

        randomize_button = ttk.Button(right_frame, text="Randomize Week's Meals", command=self.randomize_weekly_plan)
        randomize_button.pack(fill=tk.X, pady=(20, 5))

        clear_plan_button = ttk.Button(right_frame, text="Clear Week's Plan", command=self.clear_weekly_plan)
        clear_plan_button.pack(fill=tk.X)

    def update_available_meals_display(self):
        self.available_meals_listbox.delete(0, tk.END)
        for meal in sorted(self.all_meals):
            self.available_meals_listbox.insert(tk.END, meal)

    def update_weekly_plan_display(self):
        for day, meal in zip(self.days_of_week, self.weekly_plan):
            self.meal_labels[day].config(text=meal if meal else "---")

    def add_meal_from_entry(self, event=None): # Added event=None for binding
        meal_name = self.new_meal_entry.get().strip()
        if meal_name:
            if meal_name not in self.all_meals:
                self.all_meals.append(meal_name)
                self.all_meals.sort()
                self.save_meals()
                self.update_available_meals_display()
                self.new_meal_entry.delete(0, tk.END) # Clear entry field
            else:
                # No popup for duplicate, just clear entry and do nothing else
                self.new_meal_entry.delete(0, tk.END)
                # Optionally, you could provide non-popup feedback here (e.g., status bar)
                print(f"'{meal_name}' is already in the list.") # Console feedback for now
        else:
            # No popup for empty input
            # Optionally, provide non-popup feedback
            print("Meal name cannot be empty.") # Console feedback for now


    def delete_selected_meal(self):
        selected_indices = self.available_meals_listbox.curselection()
        if not selected_indices:
            # No popup for no selection
            print("No meal selected to delete.") # Console feedback for now
            return

        selected_meal = self.available_meals_listbox.get(selected_indices[0])

        # No confirmation popup - direct deletion
        if selected_meal in self.all_meals:
            self.all_meals.remove(selected_meal)
            self.save_meals()
            self.update_available_meals_display()
            # Remove from current plan if it was there
            for i, meal_in_plan in enumerate(self.weekly_plan):
                if meal_in_plan == selected_meal:
                    self.weekly_plan[i] = ""
            self.update_weekly_plan_display()

    def _secrets_sample(self, population, k):
        """
        Securely sample k unique items from population.
        Similar to random.sample but using secrets module.
        Implements Fisher-Yates shuffle for the selection part.
        """
        n = len(population)
        if not 0 <= k <= n:
            raise ValueError("Sample size k must be between 0 and population size n.")

        arr = list(population)
        # Perform a partial Fisher-Yates shuffle to pick k elements
        # We only need to shuffle the elements that will be chosen
        for i in range(k):
            # Pick an index j from i to n-1
            j = secrets.randbelow(n - i) + i
            # Swap arr[i] with arr[j]
            arr[i], arr[j] = arr[j], arr[i]
        # The first k elements are now a random sample
        return arr[:k]

    def randomize_weekly_plan(self):
        if not self.all_meals:
            # No popup for no meals
            print("No meals available to randomize.") # Console feedback for now
            return

        if len(self.all_meals) < 7:
            # Allow repeats if fewer than 7 unique meals
            self.weekly_plan = [secrets.choice(self.all_meals) for _ in range(7)]
        else:
            # Pick 7 unique meals
            self.weekly_plan = self._secrets_sample(self.all_meals, 7)

        self.update_weekly_plan_display()

    def clear_weekly_plan(self):
        self.weekly_plan = [""] * 7
        self.update_weekly_plan_display()
        # No confirmation popup

    def reroll_meal(self, day_of_week):
        if not self.all_meals:
            print("No meals available to re-roll.")
            return

        day_index = self.days_of_week.index(day_of_week)
        current_meal_for_day = self.weekly_plan[day_index]
        meals_already_planned = set(meal for i, meal in enumerate(self.weekly_plan) if i != day_index and meal)

        # Prioritize meals that are not already planned for other days
        available_meals = [
            meal for meal in self.all_meals
            if meal != current_meal_for_day and meal not in meals_already_planned
        ]

        # If no new unique meals are available, fall back to any meal (excluding the current one)
        if not available_meals:
            available_meals = [meal for meal in self.all_meals if meal != current_meal_for_day]
            if not available_meals:
                print(f"No other meals available to re-roll for {day_of_week}.")
                return

        new_meal = secrets.choice(available_meals)
        self.weekly_plan[day_index] = new_meal
        self.update_weekly_plan_display()

if __name__ == "__main__":
    root = tk.Tk()
    app = MealPlannerApp(root)
    root.mainloop()