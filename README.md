
# Website Scanner Tool

## Project info

A Python utility for scanning websites and extracting contact information from CSV data.

**URL**: https://lovable.dev/projects/152e5d30-ca47-4366-9fcd-9629697ced69

## Features

- Website status checking (working/not working)
- Extracts emails, phone numbers, LinkedIn links, and Instagram links
- Processes large CSV files efficiently using multithreading
- Detailed logging for troubleshooting

## Requirements

```
pip install requests beautifulsoup4 tqdm
```

## How to Use

1. Save the script as `website_scanner.py`
2. Prepare your CSV file with at least a "Website URL" column
3. Run the script:
   ```
   python website_scanner.py input.csv -o output.csv -w 10 -p 5
   ```

### Parameters

- `input.csv`: Your input CSV file path
- `-o, --output`: Output CSV file path (default: processed_input.csv)
- `-w, --workers`: Number of worker threads (default: 10)
- `-p, --pages`: Maximum pages to scan per website (default: 5)

## Example

```
python website_scanner.py websites.csv --output results.csv --workers 20 --pages 10
```

## Output

The script adds the following columns to your CSV:
- Status: "Working" or "Not working"
- Error: Error message if website couldn't be accessed
- Email: Extracted email addresses
- Phone: Extracted phone numbers
- LinkedIn: LinkedIn profile links
- Instagram: Instagram profile links

## How can I edit this code?

There are several ways of editing your application.

**Use Lovable**

Simply visit the [Lovable Project](https://lovable.dev/projects/152e5d30-ca47-4366-9fcd-9629697ced69) and start prompting.

Changes made via Lovable will be committed automatically to this repo.

**Use your preferred IDE**

If you want to work locally using your own IDE, you can clone this repo and push changes. Pushed changes will also be reflected in Lovable.

The only requirement is having Node.js & npm installed - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)

Follow these steps:

```sh
# Step 1: Clone the repository using the project's Git URL.
git clone <YOUR_GIT_URL>

# Step 2: Navigate to the project directory.
cd <YOUR_PROJECT_NAME>

# Step 3: Install the necessary dependencies.
npm i

# Step 4: Start the development server with auto-reloading and an instant preview.
npm run dev
```

**Edit a file directly in GitHub**

- Navigate to the desired file(s).
- Click the "Edit" button (pencil icon) at the top right of the file view.
- Make your changes and commit the changes.

**Use GitHub Codespaces**

- Navigate to the main page of your repository.
- Click on the "Code" button (green button) near the top right.
- Select the "Codespaces" tab.
- Click on "New codespace" to launch a new Codespace environment.
- Edit files directly within the Codespace and commit and push your changes once you're done.

## What technologies are used for this project?

This project is built with:

- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS

## How can I deploy this project?

Simply open [Lovable](https://lovable.dev/projects/152e5d30-ca47-4366-9fcd-9629697ced69) and click on Share -> Publish.

## I want to use a custom domain - is that possible?

We don't support custom domains (yet). If you want to deploy your project under your own domain then we recommend using Netlify. Visit our docs for more details: [Custom domains](https://docs.lovable.dev/tips-tricks/custom-domain/)
