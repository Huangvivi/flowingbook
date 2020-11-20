from flowingbook.view_models.book import BookViewModel


# Most of the codes are same with MyGifts, cuz both of the logic of this two class
# are the same
class MyWishes:
    def __init__(self, wish_counts, gifts_of_user):
        self.gifts = []
        self.__wish_counts = wish_counts
        self.__gifts = gifts_of_user
        self.gifts = self.__parse()

    def __parse(self):
        temp = []
        for gift in self.__gifts:
            temp.append(self.__matching(gift))
        return temp

    def __matching(self, gift):
        count = 0
        for wish_count in self.__wish_counts:
            if wish_count['isbn'] == gift.isbn:
                count = wish_count['count']
        r = dict(id=gift.id, book=BookViewModel(gift.book), wishes_count=count)
        return r
