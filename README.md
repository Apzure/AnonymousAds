<!-- PROJECT LOGO -->
<br />

<h3 align="center">AnonymousAds</h3>

  <p align="center">
    Targetted ads without user tracking!
    <br />
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li><a href="#methodology">Methodology</a></li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About The Project

[![Product Name Screen Shot][product-screenshot]](https://example.com)

Here's a blank template to get started: To avoid retyping too much info. Do a search and replace with your text editor for the following: `github_username`, `repo_name`, `twitter_handle`, `linkedin_username`, `email_client`, `email`, `project_title`, `project_description`

AnonymousAds is a web application that serves targeted advertising to users, without compromising user privacy.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

- Flask
- ConcreteML

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- METHODOLOGY -->

## Methodology

TBD

<!-- GETTING STARTED -->

## Getting Started

AnonymousAds is built to run on desktops.

To get a local copy of AnonymousAds up and running follow these simple steps.

### Prerequisites

Docker desktop is required to run the application.

Download Docker at [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)

We recommend having at least 6GB of RAM.

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/Apzure/AnonymousAds.git
   ```
2. Open Docker desktop
3. Enter in the terminal
   ```sh
   docker compose up
   ```
4. Open up the link [http://127.0.0.1:5000](http://127.0.0.1:5000) provided in the terminal

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->

## Usage

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Acknowledgments

We used free stock photos in our application. For more information, see `credits.txt` in our repo.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

# Anonymous Ads

1. Generates User Data (collect and compile search engine results, tiktok)
2. Encryption
3. Send to external Server [do we have to implement this?]
4. Apply transformations to process it into encrypted Tags, Categories, Keywords that help determine what ads to show a specific user
5. Send back to the user
6. Decryption
7. Add dummy tags and request the set of ads from TikTok
8. Display selected ads, with the real tags to the user

9. - On start-up Concrete ML model is trained on clear data on server side
   - Client generates public keys and sends to server
10. Search-Engine FrontEnd
    - Your Search History, sends after every 10 Requests / Button
11. ## Encryption and send to server
12. Apply Transformations on the server-side
13. Send back transformed data along with set of all tags to user
14. Decryption
15. User randomly selects dummy tags from the set of all tags
16. User requests ads from the server that include these tags

    - Concrete ML model is trained and compiled on clear data on dev side using the FHEModelDev class

    - Client generates public keys and sends to server
    - Client inputs search queries and this is saved
    - Search History is converted to "input" is sent to server
    - Server takes input and uses model to predict tags (output is encrypted)
    - Server sends encrypted prediction to Client and set of all tags
    - Client decrypts prediction, and adds noise to the prediction
    - Server gets ads
