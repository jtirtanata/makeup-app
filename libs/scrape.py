from bs4 import BeautifulSoup
import pandas as pd
def bs_scrape(soup, el, attr, many=False, attribute=None):
    q = soup.find_all(el, attr)
    if not q:
        return None
    if attribute:
        ans = [a[attribute] for a in q]
    else:
        ans = [a.text for a in q]
    if not many:
        return ans[0]
    return ans

def find_user_info(els, class_, el='span', attr=None, join=False):
    els = [e.find(el, class_=class_) for e in els]
    for i, e in enumerate(els):
        if e:
            if not attr:
                els[i] = e.text
            else:
                els[i] = e[attr]
            if join:
                els[i] = ' '.join(els[i])
        else:
            els[i] = ''
    return els

def bs_find_el(soup, el, class_, many=True, attr=None):
    obj = soup.find_all(el[0], class_=class_[0])

    for i in range(1, len(el)):
        obj = [x for x in obj if x != None]
        obj = [x.find(el[i], class_=class_[i]) for x in obj]

    obj = [x for x in obj if x != None]
    if not attr:
        return [x.text for x in obj]
    return [x[attr] for x in obj]


def scrape_users(soup, p_id):
    users={}
    users['username'] = bs_scrape(soup, 'span', {'itemprop': 'author'}, True)
    users['body'] = bs_scrape(soup, 'div', {'itemprop': 'description'}, True)
    users['title'] = bs_scrape(soup, 'span', {'class': 'BVRRReviewTitle'}, True)
    users['date'] = bs_scrape(soup, 'span', {'class':'BVRRReviewDate'}, True)
    users['not_helpful'] = bs_find_el(soup, ['span', 'span', 'span'], ['BVDI_FVNegative', 'BVDILinkSpan','BVDINumber'])
    users['helpful'] = bs_find_el(soup, ['span', 'span', 'span'], ['BVDI_FVPositive','BVDILinkSpan', 'BVDINumber'])
    users['star_count'] = bs_find_el(soup.find('div', {'id':'BVRRDisplayContentID'}), ['img'], ['BVImgOrSprite'], attr='alt')
    els = soup.find('div', {'id': 'BVRRDisplayContentID'}).find_all(class_='BVRRReviewDisplayStyle3Summary')
    users['location'] = find_user_info(els, 'BVRRUserLocation')
    users['skin_tone'] = find_user_info(els, 'BVRRContextDataValueskinTone')
    users['eye_color'] = find_user_info(els, 'BVRRContextDataValueeyeColor')
    users['status'] = find_user_info(els, 'BVRRBadgeLabel', 'div','class', True)
    users['age'] = find_user_info(els, 'BVRRContextDataValueage')
    users['product_id'] = [p_id] * len(users['username'])
    return pd.DataFrame(users)
