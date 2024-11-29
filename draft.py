class NewStockHistory:

    def __init__(self, output_folder="./Stock_DB"):
        self.logger = Logger(
            name=__class__.__name__,
            level=log_show_level,
            log_file=log_file_path,
        )
        self.logger.log_debug("Init StockHistory")
        self.output_folder = output_folder
        self.output_folder_path = Path(output_folder)
        self.output_folder_path.mkdir(parents=True, exist_ok=True)

    def __fetch_stock_history(self, stock_numbers, start):
        stock_data = {}
        tickers = yf.Tickers(" ".join(stock_numbers))

        for stock_number in stock_numbers:
            if start:
                df = tickers.tickers[stock_number].history(
                    start=start, period="max"
                )
            else:
                df = tickers.tickers[stock_number].history(period="max")
            df = df.round(2)
            stock_data[stock_number] = df

        return stock_data

    def get_stock_history(self, yf_stock_number_list, start=None):
        self.logger.log_debug(
            f"Get stock history data for {yf_stock_number_list} "
            f"start from {start}"
        )

        if isinstance(yf_stock_number_list, str):
            yf_stock_number_list = [yf_stock_number_list]

        m_thread = MutiThread(max_threads=0)
        max_group = 100
        tasks = [
            (yf_stock_number_list[i : i + max_group], start)
            for i in range(0, len(yf_stock_number_list), max_group)
        ]

        results = m_thread.run_multithreaded(self.__fetch_stock_history, tasks)

        stock_data = {}
        for result in results["result"].values():
            stock_data.update(result)

        if not results["status"]:
            self.logger.log_error(
                f"Failed to get stock history data: {results['fail_items']}"
            )

        return stock_data

    def save_stock_data_to_csv_single(self, stock_number, df):
        if ".TWO" in stock_number:
            file_name = stock_number.replace(".TWO", "") + ".csv"
        elif ".TW" in stock_number:
            file_name = stock_number.replace(".TW", "") + ".csv"

        file_full_path = self.output_folder_path / file_name
        if len(df.index) == 0:
            self.logger.log_warning(f"{stock_number} has no data")
        df.to_csv(file_full_path)

    # No one use this function
    def save_stocks_df_to_csv(self, stock_data):
        #stock_data is a dict {stock_number: df}
        tasks = []
        for stock_number, df in stock_data.items():
            tasks.append((stock_number, df))
        

        results = m_thread.run_multithreaded(
            self.save_stock_data_to_csv_single, tasks
        )
        if not results["status"]:
            self.logger.log_error(
                f"Failed to save stock data to csv: {results['fail_items']}"
            )

    # No one use this function
    def read_stock_df_from_csv(self, stock_number_list):
        if isinstance(stock_number_list, str):
            stock_number_list = [stock_number_list]

        stock_data = {}
        start_date = None
        for stock_number in stock_number_list:
            if ".TWO" in stock_number:
                file_name = stock_number.replace(".TWO", "") + ".csv"
            elif ".TW" in stock_number:
                file_name = stock_number.replace(".TW", "") + ".csv"

            file_full_path = self.output_folder_path / file_name
            if file_full_path.is_file():
                df = pd.read_csv(file_full_path, index_col="Date")
                stock_data[stock_number] = df
                if start_date is None:
                    start_date = df.index[-1].split(" ")[0]
                else:
                    start_date = min(start_date, df.index[-1].split(" ")[0])
            else:
                self.logger.log_info(f"{stock_number} has no data")
                stock_data[stock_number] = pd.DataFrame()
        return stock_data, start_date

    def merge_stock_data(self, stock_data, stock_data_new):
        # merge stock_data and stock_data_new and some stock_num not in the stock_data_new or stock_data
        # and return the merged stock_data {stock_number: df}
        stock_data_merged = {}
        stock_data_keys = set(stock_data.keys())
        stock_data_new_keys = set(stock_data_new.keys())
        all_stock_numbers = stock_data_keys.union(stock_data_new_keys)
        for stock_number in all_stock_numbers:
            if stock_number in stock_data_new_keys:
                if stock_number in stock_data_keys:
                    stock_data_merged[stock_number] = pd.concat(
                        [stock_data[stock_number], stock_data_new[stock_number]]
                    ).drop_duplicates()
                else:
                    stock_data_merged[stock_number] = stock_data_new[stock_number]
            else:
                stock_data_merged[stock_number] = stock_data[stock_number]
        return stock_data_merged

    def update_merge_save_stock_data(self, stock_number_list):
        self.logger.log_debug(f"Update stock data for {stock_number_list}")
        stock_data, start_date = self.read_stock_df_from_csv(stock_number_list)
        stock_data_new = self.get_stock_history(stock_number_list, start_date)
        # merge stock_data and stock_data_new and some stock_num not in the stock_data_new or stock_data
        # save the merged data to csv
        stock_data_merged = self.merge_stock_data(stock_data, stock_data_new)
        self.save_stocks_df_to_csv(stock_data_merged)

