import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request

app = Flask(__name__)

def get_mentions(base_url, horse_name):
    mentions = []
    page_number = 1

    while True:
        # Construct the URL for the current page
        url = f"{base_url}/page{page_number}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all comments using the selector
            comments = soup.find_all('div', class_='js-post__content-text restore h-wordwrap')

            for comment_div in comments:
                comment_text = ""
                for child in comment_div.children:
                    if child.name and child.name == "div" and child.has_attr("class") and "bbcode_container" in child["class"]:
                        continue
                    if not child.name:
                        comment_text += child.string.strip() if child.string else ""

                # Extract username and date
                username_tag = comment_div.find_previous('a', attrs={"data-vbnamecard": True})
                username = username_tag.text if username_tag else "Unknown"
                date_tag = comment_div.find_previous('time', itemprop="dateCreated")
                date = date_tag.text if date_tag else "Unknown Date"
                link_tag = comment_div.find_previous('a', class_='b-post__count js-show-post-link')
                link = link_tag['href'] if link_tag else 'No link'

                # Case-insensitive search
                if horse_name.lower() in comment_text.lower() and len(mentions) < 15:
                 mentions.append(f'Posted by: {username} on {date}| Page: {page_number}<br>{comment_text}<br> Link: {link}<br><br><br>')



            if len(mentions) >= 15:
                break

            # Check if a "next" page exists
            next_page = soup.find('a', class_='arrow right-arrow', title='Next Page')
            if not next_page:
                break

            page_number += 1

        except requests.RequestException as e:
            print(f"Error fetching page {page_number}. Error: {e}")
            break

    return mentions

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        base_url = request.form.get('forum_url')
        horse_name = request.form.get('horse_name')
        mentions = get_mentions(base_url, horse_name)
        return render_template('results.html', mentions=mentions)
    return render_template('index.html')




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)



