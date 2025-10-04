# ==========================================
# 🍳 Recipe Search & Recommendation System (GUI Version)
# Developed by: Group 16
# ==========================================

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import tkinter as tk
from tkinter import scrolledtext, messagebox

# ------------------------------------------
# Step 1: Load Dataset
# ------------------------------------------
print("Loading dataset...")

data = pd.read_csv("recipes.csv")

# Fix column names to match the actual CSV structure
if 'RecipeIngredientParts' in data.columns:
    data.rename(columns={'RecipeIngredientParts': 'ingredients'}, inplace=True)
if 'Name' in data.columns:
    data.rename(columns={'Name': 'name'}, inplace=True)

# Remove null values
data = data.dropna(subset=['ingredients', 'name']).reset_index(drop=True)

# Clean up ingredients
def clean_ingredients(ingredient_string):
    if pd.isna(ingredient_string):
        return ""
    cleaned = str(ingredient_string).replace('c(', '').replace(')', '')
    ingredients = cleaned.replace('"', '').replace("'", '').split(',')
    cleaned_ingredients = [ing.strip().lower() for ing in ingredients if ing.strip()]
    return ' '.join(cleaned_ingredients)

print("Cleaning ingredient data...")
data['ingredients'] = data['ingredients'].apply(clean_ingredients)
data = data[data['ingredients'].str.len() > 0].reset_index(drop=True)

print("Dataset loaded successfully! Total Recipes:", len(data))

# ------------------------------------------
# Step 2: Convert Ingredients to Vectors (TF-IDF)
# ------------------------------------------
print("Converting ingredients into numerical features...")
vectorizer = TfidfVectorizer(stop_words='english')
ingredient_vectors = vectorizer.fit_transform(data['ingredients'])
print("Ingredients vectorized successfully!")

# ------------------------------------------
# Step 3: Recommendation Function
# ------------------------------------------
def recommend_recipes(user_input, top_n=10):
    user_input_cleaned = ' '.join([ing.strip().lower() for ing in user_input.split(',')])
    user_vector = vectorizer.transform([user_input_cleaned])
    similarity = cosine_similarity(user_vector, ingredient_vectors)
    sim_scores = list(enumerate(similarity[0]))
    sim_scores = [(i, score) for i, score in sim_scores if score > 0.01]
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    top_indices = [i[0] for i in sim_scores[:top_n]]
    if not top_indices:
        return pd.DataFrame()
    recommended = data.iloc[top_indices][['name', 'ingredients']].reset_index(drop=True)
    similarity_scores = [sim_scores[i][1] for i in range(len(top_indices))]
    recommended['similarity_score'] = similarity_scores
    return recommended

# ------------------------------------------
# Step 4: GUI (Tkinter)
# ------------------------------------------
def get_recommendations():
    user_input = entry.get().strip()
    if not user_input:
        messagebox.showwarning("Input Error", "Please enter some ingredients!")
        return
    
    results = recommend_recipes(user_input)
    text_box.config(state='normal')
    text_box.delete(1.0, tk.END)
    
    if results.empty:
        text_box.insert(tk.END, "No recipes found! Try different ingredients.\n")
        text_box.insert(tk.END, "Tip: Use common words like 'chicken', 'tomato', 'onion', 'garlic'\n")
    else:
        text_box.insert(tk.END, f"Top {len(results)} Recommended Recipes:\n\n")
        for i, row in results.iterrows():
            text_box.insert(tk.END, f"{i+1}. {row['name']}\n")
            text_box.insert(tk.END, f"   Ingredients: {row['ingredients'][:120]}...\n")
            text_box.insert(tk.END, f"   Similarity Score: {row['similarity_score']:.3f}\n")
            text_box.insert(tk.END, "-" * 80 + "\n")
    
    text_box.config(state='disabled')

# Main window setup
root = tk.Tk()
root.title("🍳 Recipe Search & Recommendation System - Group 16")
root.geometry("700x600")
root.config(bg="#f9f9f9")

title = tk.Label(root, text="Recipe Recommendation System", font=("Helvetica", 16, "bold"), bg="#f9f9f9", fg="#333")
title.pack(pady=10)

subtitle = tk.Label(root, text="Enter ingredients (comma separated):", font=("Arial", 12), bg="#f9f9f9")
subtitle.pack()

entry = tk.Entry(root, width=80, font=("Arial", 12))
entry.pack(pady=10)

button = tk.Button(root, text="Search Recipes", command=get_recommendations, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
button.pack(pady=10)

text_box = scrolledtext.ScrolledText(root, width=80, height=25, wrap=tk.WORD, font=("Consolas", 10))
text_box.pack(pady=10)
text_box.config(state='disabled')

root.mainloop()
