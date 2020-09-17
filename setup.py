from app.models import AdminsList
def setup():
    u=AdminsList.query.filter_by(email=os.environ.get('SUPER')).first()
    if not u:
        a=AdminsList(email=os.environ.get('SUPER'))
        res=a.add()
    return res
if __name__=='__main__':
    setup()