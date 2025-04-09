import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import paramiko
import os
from datetime import datetime
from bs4 import BeautifulSoup # pip3 install beautifulsoup4

# variable to store the saved item
saved_item = None

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
        <link rel="stylesheet" href="styles.css">
    </head>
    <body>
        <header>
            <h5><a href="index.html">MOUTHS MADE WORDLESS</a></h5>
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
    sftp.put(new_post_filename, f'{ config["publicFilePath"] }{new_post_filename}')

    # Add new blog post to index.html
    new_article = soup.new_tag('article', **{'class': 'blog-post'})
    new_link = soup.new_tag('a', href=f'./{new_post_filename}', **{'class': 'blog-post-link'})
    new_div = soup.new_tag('div', **{'class': 'blog-post-content'})
    new_img = soup.new_tag('img', src=cover_image, alt='Missing Image')
    new_h2 = soup.new_tag('h2')
    new_h2.string = title
    new_p = soup.new_tag('p')
    new_p.string = f"{date}"

    new_div.append(new_img)
    new_div.append(new_h2)
    new_div.append(new_p)
    new_link.append(new_div)
    new_article.append(new_link)
    soup.find(id='blog-posts').append(new_article)

    # Save updated index.html
    with open('index.html', 'w') as f:
        f.write(str(soup))

    # Upload updated index.html
    sftp.put('index.html', f"{config['publicFilePath']}index.html")

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
            image_tag = f'<img src="images/{image_filename}" alt="Missing Image"><p class="image-caption"><i>Image Caption Here</i></p>'
            content_text.insert(tk.INSERT, image_tag)

    def insert_home_image():
        # Get the local path of the image
        image_path = tk.filedialog.askopenfilename(title="Select Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])

        # send the image to the images folder on the server
        image_filename = image_path.split('/')[-1]
        sftp.put(image_path, f'{ config["publicFilePath"] }images/{image_filename}')

        # set the cover image to the image path
        cover_image_entry.delete(0, tk.END)
        cover_image_entry.insert(0, f'images/{image_filename}')

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
    

    

# List existing blog posts
def list_blog_posts():
    # Find all blog posts in index.html
    posts = soup.find_all('article', class_='blog-post')
    post_titles = [post.find('h2').text for post in posts]
    return post_titles

def remove_blog_post(title):
    # Find the blog post by title
    posts = soup.find_all('article', class_='blog-post')
    for post in posts:
        if post.find('h2').text == title:
            # get the name of the html file
            link = post.find('a')['href'].split('/')[-1]
            # remove the blog post file 
            sftp.remove(f'{ config["publicFilePath"] }{link}')
            print(f"Removed blog post file: {link}")
            
            # remove the blog post from the index.html
            post.decompose()
            print(f"Removed blog post: {title}")
            break

    # Save updated index.html
    with open('index.html', 'w') as f:
        f.write(str(soup))

    # Upload updated index.html
    sftp.put('index.html', f'{ config["publicFilePath"] }index.html')

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
    root.geometry("800x600")

    tk.Label(root, text="Existing Blog Posts:").pack()
    post_listbox = tk.Listbox(root)
    post_listbox.pack()
    for post in list_blog_posts():
        post_listbox.insert(tk.END, post)

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