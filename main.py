if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()   # requerido para spawn en Windows
    from ui.app import App
    App().run()