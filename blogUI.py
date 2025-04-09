import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import paramiko
import os
from datetime import datetime
from bs4 import BeautifulSoup # pip3 install beautifulsoup4
import json
import re

# variable to store the saved item
saved_item = None

# variable to cycle through the list of posts
post_index = 0 # 0 aka the first post in the list
post_page_size = 10 # number of posts to show at a time


# Load configuration
config = {}
with open('config.txt', 'r') as f:
    for line in f:
        name, value = line.strip().split('=')
        config[name] = value

    # check if config['publicFilePath'] ends with a slash
    if not config['publicFilePath'].endswith('/'):
        config['publicFilePath'] += '/'

    print("Configuration loaded successfully.")
    print(config)

# Get port number from configuration
port = int(config.get('port', 22))  # Default to port 22 if not specified

# Connect to the server
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(config['hostname'], port=port, username=config['username'], password=config['password'])

sftp = ssh.open_sftp()

# Download index.html
sftp.get(f'{ config["publicFilePath"] }index.html', 'index.html')

# Parse index.html 
with open('index.html', 'r') as f:
    soup = BeautifulSoup(f, 'html.parser')

# Function to add new blog post
def add_blog_post(title, date, content, cover_image):
    # Create new blog post HTML file
    new_post_filename = f"post_{datetime.now().strftime('%Y%m%d%H%M%S')}.html"
    new_post_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <link rel="stylesheet" href="../styles.css">
    </head>
    <body>
        <header>
            <h5><a href="../index.html">MOUTHS MADE WORDLESS</a></h5>
            <h1>{title}</h1>
        </header>
        <section>
            <p>{date}</p>
            <div class="blog-post-page-content">{content}</div>
        </section>
    </body>
    </html>
    """
    with open(new_post_filename, 'w') as f:
        f.write(new_post_html)


    # Upload new blog post HTML file to the posts folder
    sftp.put(new_post_filename, f'{ config["publicFilePath"] }posts/{new_post_filename}')
    
    meta_path = f'{config["publicFilePath"]}posts/meta.json'
    local_meta_tmp = 'meta_tmp.json'

    # 1. Check if the remote file exists. If not, create it with an empty list.
    try:
        sftp.stat(meta_path)
    except FileNotFoundError:
        with open(local_meta_tmp, 'w') as f:
            json.dump([], f, indent=4)
        sftp.put(local_meta_tmp, meta_path)

    # 2. Download the file temporarily
    sftp.get(meta_path, local_meta_tmp)

    # 3. Load the existing JSON list
    with open(local_meta_tmp, 'r') as f:
        try:
            posts = json.load(f)
            if not isinstance(posts, list):
                raise ValueError("meta.json is not a list")
        except json.JSONDecodeError:
            posts = []

    # 4. Append the new post safely
    new_post = {
        "filename": new_post_filename,
        "title": title,
        "date": date,
        "cover_image": cover_image
    }
    # append the new post to the start of the list of posts
    posts.insert(0, new_post)

    # 5. Write updated list back to local file
    with open(local_meta_tmp, 'w') as f:
        json.dump(posts, f, indent=4)

    # 6. Upload back to server
    sftp.put(local_meta_tmp, meta_path)

    # 7. Clean up
    os.remove(local_meta_tmp)
    
    # Clean up local files
    os.remove(new_post_filename)

# GUI for adding new blog post
def prompt_for_blog_post():
    def submit():
        title = title_entry.get()
        date = date_entry.get()
        content = content_text.get("1.0", tk.END).strip()
        cover_image = cover_image_entry.get()

        # Set each paragraph into the <p> tag
        content = content.replace('\n', '</p><p>')
        content = f'<p>{content}</p>'

        if title and date and content:
            add_blog_post(title, date, content, cover_image)
            messagebox.showinfo("Success", "Blog post added successfully!")
            prompt_root.destroy()
        else:
            messagebox.showwarning("Input Error", "All fields are required!")

        # Refresh the listbox
        root.destroy()
        main()
    
    def insert_image():
        # Get the local path of the image
        image_path = tk.filedialog.askopenfilename(title="Select Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])

        # send the image to the images folder on the server
        image_filename = image_path.split('/')[-1]
        sftp.put(image_path, f'{ config["publicFilePath"] }images/{image_filename}')
        
        if image_path:
            image_tag = f'<img src="../images/{image_filename}" alt="Missing Image"><p class="image-caption"><i>Image Caption Here</i></p>'
            content_text.insert(tk.INSERT, image_tag)

    def insert_home_image():
        # Get the local path of the image
        image_path = tk.filedialog.askopenfilename(title="Select Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])

        # send the image to the images folder on the server
        image_filename = image_path.split('/')[-1]
        sftp.put(image_path, f'{ config["publicFilePath"] }images/{image_filename}')

        # set the cover image to the image path
        cover_image_entry.delete(0, tk.END)
        cover_image_entry.insert(0, f'./images/{image_filename}')

    prompt_root = tk.Tk()
    prompt_root.title("New Blog Post")

    tk.Label(prompt_root, text="Cover Image Path:").pack()
    cover_image_entry = tk.Entry(prompt_root)
    cover_image_entry.pack()
    tk.Button(prompt_root, text="Insert Cover Image", command=insert_home_image).pack()

    tk.Label(prompt_root, text="Blog Post Title:").pack()
    title_entry = tk.Entry(prompt_root)
    title_entry.pack()

    tk.Label(prompt_root, text="Blog Post Date (e.g., January 01, 2025):").pack()
    date_entry = tk.Entry(prompt_root)
    date_entry.pack()

    tk.Label(prompt_root, text="Blog Post Content:").pack()
    content_text = tk.Text(prompt_root, height=15)
    content_text.pack()

    tk.Button(prompt_root, text="Insert Image", command=insert_image).pack()

    tk.Button(prompt_root, text="Submit", command=submit).pack()

    prompt_root.mainloop()
    

def remove_blog_post(title):
    if not title:
        messagebox.showwarning("Selection Error", "No blog post selected!")
        return

    # Confirm deletion
    if not messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the blog post '{title}'?"):
        return

    meta_path = f'{config["publicFilePath"]}posts/meta.json'
    local_meta_tmp = 'meta_tmp.json'

    try:
        # Download the meta.json file temporarily
        sftp.get(meta_path, local_meta_tmp)

        # Load the existing JSON list
        with open(local_meta_tmp, 'r') as f:
            posts = json.load(f)
            if not isinstance(posts, list):
                raise ValueError("meta.json is not a list")

        # Find the post to remove
        post_to_remove = next((post for post in posts if post.get("title") == title), None)
        if not post_to_remove:
            messagebox.showerror("Error", "Blog post not found in meta.json!")
            return

        # Get the filename of the post
        post_filename = post_to_remove.get("filename")
        if not post_filename:
            messagebox.showerror("Error", "Post filename not found!")
            return

        # Delete the post file from the server
        try:
            sftp.remove(f'{config["publicFilePath"]}posts/{post_filename}')
        except FileNotFoundError:
            print(f"Post file {post_filename} not found on the server. Skipping deletion.")

        # Remove the post from the meta.json list
        posts = [post for post in posts if post.get("title") != title]

        # Write updated list back to local file
        with open(local_meta_tmp, 'w') as f:
            json.dump(posts, f, indent=4)

        # Upload the updated meta.json file back to the server
        sftp.put(local_meta_tmp, meta_path)

        # Remove the local temporary file
        os.remove(local_meta_tmp)

        messagebox.showinfo("Success", f"Blog post '{title}' removed successfully!")

    except FileNotFoundError:
        messagebox.showerror("Error", "meta.json not found on the server!")
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Error decoding meta.json. Please check its format.")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")
    finally:
        # Clean up local temporary file if it exists
        if os.path.exists(local_meta_tmp):
            os.remove(local_meta_tmp)

    # Refresh the listbox
    root.destroy()
    main()
    


# Function to handle item selection
def save_selection(listbox):
    global saved_item
    # Get the index of the selected item
    selected_index = listbox.curselection()
    if selected_index:  # Ensure an item is selected
        selected_item = listbox.get(selected_index)
        print(f"Selected Item: {selected_item}")
        # Save the item (e.g., append to a list)
        saved_item = selected_item
        print(f"Saved Items: {saved_item}")



# Main function
def main():
    global root
    root = tk.Tk()
    root.title("Blog Post Manager")
    root.geometry("300x300")

    tk.Label(root, text="Existing Blog Posts:").pack()
    post_listbox = tk.Listbox(root)
    post_listbox.pack()

    # create the list of posts from the meta.json file
    meta_path = f'{config["publicFilePath"]}posts/meta.json'
    local_meta_tmp = 'meta_tmp.json'

    # Download the meta.json file temporarily
    try:
        sftp.get(meta_path, local_meta_tmp)
        with open(local_meta_tmp, 'r') as f:
            posts = json.load(f)
            if isinstance(posts, list):
                for post in posts:
                    post_listbox.insert(tk.END, post.get("title", "Untitled Post"))
    except FileNotFoundError:
        print("meta.json not found on the server. No posts to display.")
    except json.JSONDecodeError:
        print("Error decoding meta.json. Please check its format.")
    finally:
        if os.path.exists(local_meta_tmp):
            os.remove(local_meta_tmp)
            


    # bind the listbox to the save_selection function aka saves the selected item within the list of posts
    post_listbox.bind("<ButtonRelease-1>", lambda event: save_selection(post_listbox))

    # create a new button to add a new blog post
    tk.Button(root, text="Add New Blog Post", command=prompt_for_blog_post).pack()

    # create a new button to remove the selected blog post
    tk.Button(root, text="Remove Selected Blog Post", command=lambda: remove_blog_post(saved_item)).pack()

    root.mainloop()

if __name__ == "__main__":
    main()

# Close connections
sftp.close()
ssh.close()