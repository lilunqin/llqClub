from app import configured_app

if __name__ == '__main__':
    a = configured_app()
    # 生成配置并且运行程序
    a.run(
        debug=True,
        host='localhost',
        port=3000,
    )
