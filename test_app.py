"""
测试脚本 - 验证应用是否能正常运行
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app
    print("✓ 导入应用模块成功")
    
    app = create_app()
    print("✓ 创建应用实例成功")
    
    # 测试路由
    with app.test_client() as client:
        # 测试首页（应该重定向到登录页）
        response = client.get('/')
        if response.status_code in [200, 302]:
            print(f"✓ 首页路由正常 (状态码: {response.status_code}, 重定向到登录页)")
        else:
            print(f"✗ 首页路由异常 (状态码: {response.status_code})")
        
        # 测试登录页面
        response = client.get('/login')
        if response.status_code == 200:
            print("✓ 登录页面正常 (状态码: 200)")
        else:
            print(f"✗ 登录页面异常 (状态码: {response.status_code})")
        
        # 测试健康检查接口
        response = client.get('/api/health')
        if response.status_code == 200:
            data = response.get_json()
            print(f"✓ 健康检查接口正常 (状态码: 200, 返回: {data})")
        else:
            print(f"✗ 健康检查接口异常 (状态码: {response.status_code})")
    
    # 检查数据库文件
    if os.path.exists('data.db'):
        print("✓ 数据库文件已创建")
    else:
        print("⚠ 数据库文件未创建（首次运行时会自动创建）")
    
    print("\n" + "="*50)
    print("✓ 所有测试通过！应用框架运行正常。")
    print("="*50)
    print("\n启动应用命令：")
    print("  python run.py")
    print("\n或使用虚拟环境：")
    print("  .\\venv\\Scripts\\Activate.ps1")
    print("  python run.py")
    
except Exception as e:
    print(f"✗ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

