from flowingbook.utils.enums import PendingStatus


class TradeInfo:
    def __init__(self, goods):
        self.total = 0
        self.trades = []
        self.__parse(goods)

    def __parse(self, goods):
        self.total = len(goods)
        self.trades = [self.__map_to_trade(single) for single in goods]

    def __map_to_trade(self, single):
        if single.create_datetime:
            time = single.create_datetime.strftime("%Y-%m-%d")
        else:
            time = "未知"

        return dict(user_name=single.user.nickname, time=time, id=single.id)


class TradeCollection:
    def __init__(self, trades, current_user_id):
        self.data = []
        self.__parse(trades, current_user_id)

    def __parse(self, trades, current_user_id):
        for trade in trades:
            temp = TradeViewModel(trade, current_user_id)
            self.data.append(temp.data)


class TradeViewModel:
    def __init__(self, trade, current_user_id):
        self.data = {}
        self.data = self.__parse(trade, current_user_id)

    @staticmethod
    def requester_or_gifter(trade, current_user_id):
        if trade.requester_id == current_user_id:
            you_are = 'requester'
        else:
            you_are = 'gifter'
        return you_are

    def __parse(self, trade, current_user_id):
        you_are = self.requester_or_gifter(trade, current_user_id)
        pending_status_str = PendingStatus.pending_str(trade.pending, you_are)
        r = {
            'you_are': you_are,
            'trade_id': trade.id,
            'book_title': trade.book_title,
            'book_author': trade.book_author,
            'book_img': trade.book_img,
            'date': trade.create_datetime.strftime('%Y-%m-%d'),
            'operator': trade.requester_nickname if you_are != 'requester' else trade.gifter_nickname,
            'message': trade.message,
            'address': trade.address,
            'status_str': pending_status_str,
            'recipient_name': trade.recipient_name,
            'mobile': trade.mobile,
            'status': trade.pending
        }

        return r