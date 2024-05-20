import asyncio
import datetime
import subprocess


async def runcmd(cmd, verbose=True):
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True
    )
    std_out, std_err = process.communicate()
    if verbose:
        print(std_out.strip(), std_err)
    return std_out.strip()


async def download_data():
    today = datetime.date.today().strftime("%Y-%m-%d")
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime(
        "%Y-%m-%d"
    )
    past_date = datetime.date.today() - datetime.timedelta(days=2)

    while True:
        # Check if today's file is empty
        df_data = await runcmd(
            f"cat {today} || wget --no-check-certificate https://www.nepalstock.com.np/api/nots/market/export/todays-price/{today}",
            verbose=False,
        )
        print(today)
        if df_data.strip() == "":
            # Today's file is empty, let's try yesterday
            df_data = await runcmd(
                f"cat {yesterday} || wget --no-check-certificate https://www.nepalstock.com.np/api/nots/market/export/todays-price/{yesterday}",
                verbose=False,
            )
            print(yesterday)
            if df_data.strip() == "":
                # Yesterday's file is also empty, fetch past day's data
                past_date_str = past_date.strftime("%Y-%m-%d")
                df_data = await runcmd(
                    f"cat {past_date_str} || wget --no-check-certificate https://www.nepalstock.com.np/api/nots/market/export/todays-price/{past_date_str}",
                    verbose=False,
                )
                # Update past_date for next iteration
                past_date -= datetime.timedelta(days=1)
                print(past_date)
                # Sleep for some time to avoid flooding requests
                await asyncio.sleep(5)  # Adjust sleep time as needed
            else:
                break  # Exit loop if yesterday's data is found
        else:
            break  # Exit loop if today's data is found
    # print(df_data)
    return df_data


async def main():
    await download_data()


# Example usage
asyncio.run(main())
