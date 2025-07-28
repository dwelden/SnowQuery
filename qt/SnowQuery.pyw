from FakeModel import Model
from SnowQueryView import View
from SnowQueryPresenter import Presenter

def main():
    ''' Initialize model, view, and presenter and show window '''

    model = Model()
    view = View()
    Presenter(model, view)

    # Show window and begin event loop
    view.show()

if __name__ == '__main__':
    main()