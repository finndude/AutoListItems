import tkinter as tk
from tkinter import messagebox
import os
import glob
import time
import pyautogui
from playwright.sync_api import sync_playwright


def run_listing(title, starting_price, buy_price, description, condition,
                 condition_description, img_count, screen_width, screen_height):
    """condition: True = New, False = Used"""

    downloads = "C:/Users/Finle/Downloads"
    files = glob.glob(os.path.join(downloads, "*"))
    files.sort(key=os.path.getmtime, reverse=True)  # newest first
    recent_images = files[:img_count]

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir="C:/Users/Finle/AppData/Local/Google/Chrome/User Data/Default",
            channel="chrome",
            headless=False
        )
        page = browser.new_page()

        time.sleep(1)  # let the window fully open before snapping
        pyautogui.hotkey('win', 'left')

        page.goto(
            "https://www.ebay.co.uk/sl/prelist/identify?sr=sug&title=Test&isUid=false"
            "&sssr=shstart&radixTrackingId=b9232581-4ce7-4e13-8442-7f593c82cca9"
        )

        page.click("input[placeholder='Enter a category value']")
        input("Select the category manually in the browser, then press enter here to continue...")

        if page.locator("text=Continue without match").is_visible():
            page.click("text=Continue without match")

        if condition:
            page.check("input[value='1000']")
        else:
            page.check("input[value='3000']")

        page.click("text=Continue to listing")
        page.set_input_files("#fehelix-uploader", recent_images)
        page.wait_for_timeout(2000)
        page.fill("input[name='title']", title)

        if not condition:
            page.fill("textarea[name='itemConditionDescription']", condition_description)

        frame = page.frame_locator("#se-rte-frame__summary")
        frame.locator("div[aria-label='Description']").wait_for(timeout=10000)
        frame.locator("div[aria-label='Description']").click()
        page.keyboard.type(description)

        page.fill("input[name='startPrice']", str(starting_price))
        page.fill("input[name='price']", str(buy_price))
        page.check("input[name='immediatePay']")
        page.click("button[name='FLAT_RATE_ONLY']")
        page.click("button[name='itemOrigin.Country of Origin']")
        page.fill("input[name='search-box-itemOriginCountryofOrigin']", "United Kingdom")
        page.click("div.menu__item:has-text('United Kingdom')")

        input("Press enter in this console window to close the browser...")


def on_submit():
    title = title_entry.get()[:80]
    description = description_entry.get("1.0", "end").strip()
    condition = condition_var.get() == "New"
    condition_description = condition_desc_entry.get()[:1000]

    try:
        starting_price = float(starting_price_entry.get())
        buy_price = float(buy_price_entry.get())
        img_count = int(img_count_entry.get())
    except ValueError:
        messagebox.showerror("Invalid input", "Prices and image count must be numbers.")
        return

    if not title:
        messagebox.showerror("Invalid input", "Title is required.")
        return

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    root.destroy()  # close the GUI, then run the automation
    run_listing(title, starting_price, buy_price, description, condition,
                condition_description, img_count, screen_width, screen_height)


root = tk.Tk()
root.title("eBay Lister")
root.geometry("400x520")

tk.Label(root, text="Title (max 80 chars)").pack(anchor="w", padx=10, pady=(10, 0))
title_entry = tk.Entry(root, width=50)
title_entry.pack(padx=10)

tk.Label(root, text="Starting auction price").pack(anchor="w", padx=10, pady=(10, 0))
starting_price_entry = tk.Entry(root, width=50)
starting_price_entry.pack(padx=10)

tk.Label(root, text="Buy It Now price").pack(anchor="w", padx=10, pady=(10, 0))
buy_price_entry = tk.Entry(root, width=50)
buy_price_entry.pack(padx=10)

tk.Label(root, text="Description").pack(anchor="w", padx=10, pady=(10, 0))
description_entry = tk.Text(root, width=48, height=4)
description_entry.pack(padx=10)

def toggle_condition_description():
    if condition_var.get() == "Used":
        condition_desc_frame.pack(anchor="w", padx=10, fill="x", after=condition_frame)
    else:
        condition_desc_frame.pack_forget()


tk.Label(root, text="Condition").pack(anchor="w", padx=10, pady=(10, 0))
condition_var = tk.StringVar(value="New")
condition_frame = tk.Frame(root)
condition_frame.pack(anchor="w", padx=10)
tk.Radiobutton(condition_frame, text="New", variable=condition_var, value="New",
               command=toggle_condition_description).pack(side="left")
tk.Radiobutton(condition_frame, text="Used", variable=condition_var, value="Used",
               command=toggle_condition_description).pack(side="left")

condition_desc_frame = tk.Frame(root)
tk.Label(condition_desc_frame, text="Condition description").pack(anchor="w", pady=(10, 0))
condition_desc_entry = tk.Entry(condition_desc_frame, width=50)
condition_desc_entry.pack()
# hidden by default since "New" is selected initially

tk.Label(root, text="Number of images to upload").pack(anchor="w", padx=10, pady=(10, 0))
img_count_entry = tk.Entry(root, width=50)
img_count_entry.pack(padx=10)

tk.Button(root, text="Submit", command=on_submit, bg="#0064D2", fg="white",
          font=("Arial", 11, "bold")).pack(pady=20)

root.mainloop()