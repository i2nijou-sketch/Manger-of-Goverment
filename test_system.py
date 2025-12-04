"""
系统功能测试脚本
"""
import requests
import json
import sys

BASE_URL = 'http://localhost:5000'

def test_health():
    """测试健康检查接口"""
    print("\n[测试1] 健康检查接口...")
    try:
        response = requests.get(f'{BASE_URL}/api/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 健康检查通过: {data.get('message')}")
            return True
        else:
            print(f"✗ 健康检查失败: 状态码 {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 健康检查失败: {str(e)}")
        return False

def test_login_page():
    """测试登录页面"""
    print("\n[测试2] 登录页面...")
    try:
        response = requests.get(f'{BASE_URL}/login', timeout=5)
        if response.status_code == 200:
            print("✓ 登录页面可访问")
            return True
        else:
            print(f"✗ 登录页面访问失败: 状态码 {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 登录页面访问失败: {str(e)}")
        return False

def test_login():
    """测试登录功能"""
    print("\n[测试3] 登录功能...")
    try:
        # 创建会话
        session = requests.Session()
        
        # 测试登录
        login_data = {
            'username': 'admin',
            'password': 'admin123',
            'remember': False
        }
        
        response = session.post(
            f'{BASE_URL}/login',
            json=login_data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✓ 登录成功: {data.get('message')}")
                print(f"  用户: {data.get('user', {}).get('username')}")
                print(f"  角色: {data.get('user', {}).get('role')}")
                return session
            else:
                print(f"✗ 登录失败: {data.get('message')}")
                return None
        else:
            print(f"✗ 登录请求失败: 状态码 {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ 登录测试失败: {str(e)}")
        return None

def test_dashboard(session):
    """测试后台管理首页"""
    print("\n[测试4] 后台管理首页...")
    try:
        response = session.get(f'{BASE_URL}/dashboard', timeout=5)
        if response.status_code == 200:
            print("✓ 后台管理首页可访问")
            return True
        else:
            print(f"✗ 后台管理首页访问失败: 状态码 {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 后台管理首页测试失败: {str(e)}")
        return False

def test_current_user(session):
    """测试获取当前用户信息"""
    print("\n[测试5] 获取当前用户信息...")
    try:
        response = session.get(f'{BASE_URL}/api/current_user', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                user = data.get('data', {})
                print(f"✓ 获取用户信息成功")
                print(f"  用户名: {user.get('username')}")
                print(f"  真实姓名: {user.get('real_name')}")
                print(f"  角色: {user.get('role_name')}")
                return True
            else:
                print(f"✗ 获取用户信息失败: {data.get('message')}")
                return False
        else:
            print(f"✗ 获取用户信息请求失败: 状态码 {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 获取用户信息测试失败: {str(e)}")
        return False

def test_users_api(session):
    """测试用户管理API"""
    print("\n[测试6] 用户管理API...")
    try:
        response = session.get(f'{BASE_URL}/api/users', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                users = data.get('data', [])
                print(f"✓ 获取用户列表成功: 共 {len(users)} 个用户")
                for user in users[:3]:  # 只显示前3个
                    print(f"  - {user.get('username')} ({user.get('role_name')})")
                return True
            else:
                print(f"✗ 获取用户列表失败: {data.get('message')}")
                return False
        else:
            print(f"✗ 用户管理API请求失败: 状态码 {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 用户管理API测试失败: {str(e)}")
        return False

def test_roles_api(session):
    """测试角色管理API"""
    print("\n[测试7] 角色管理API...")
    try:
        response = session.get(f'{BASE_URL}/api/roles', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                roles = data.get('data', [])
                print(f"✓ 获取角色列表成功: 共 {len(roles)} 个角色")
                for role in roles:
                    print(f"  - {role.get('name')} ({role.get('code')})")
                return True
            else:
                print(f"✗ 获取角色列表失败: {data.get('message')}")
                return False
        else:
            print(f"✗ 角色管理API请求失败: 状态码 {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 角色管理API测试失败: {str(e)}")
        return False

def test_settings_api(session):
    """测试系统设置API"""
    print("\n[测试8] 系统设置API...")
    try:
        response = session.get(f'{BASE_URL}/api/settings', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                settings = data.get('data', {})
                print(f"✓ 获取系统设置成功")
                if 'app_name' in settings:
                    print(f"  应用名称: {settings['app_name'].get('value')}")
                return True
            else:
                print(f"✗ 获取系统设置失败: {data.get('message')}")
                return False
        else:
            print(f"✗ 系统设置API请求失败: 状态码 {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 系统设置API测试失败: {str(e)}")
        return False

def test_logout(session):
    """测试退出登录"""
    print("\n[测试9] 退出登录...")
    try:
        response = session.get(f'{BASE_URL}/logout', allow_redirects=False, timeout=5)
        if response.status_code in [302, 200]:
            print("✓ 退出登录成功")
            return True
        else:
            print(f"✗ 退出登录失败: 状态码 {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 退出登录测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("政企智能舆情分析报告生成智能体应用系统 - 功能测试")
    print("=" * 60)
    
    results = []
    
    # 基础功能测试
    results.append(("健康检查", test_health()))
    results.append(("登录页面", test_login_page()))
    
    # 登录测试
    session = test_login()
    results.append(("登录功能", session is not None))
    
    if session:
        # 需要登录的功能测试
        results.append(("后台管理首页", test_dashboard(session)))
        results.append(("获取当前用户", test_current_user(session)))
        results.append(("用户管理API", test_users_api(session)))
        results.append(("角色管理API", test_roles_api(session)))
        results.append(("系统设置API", test_settings_api(session)))
        results.append(("退出登录", test_logout(session)))
    
    # 测试结果汇总
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name:20s} {status}")
    
    print("=" * 60)
    print(f"总计: {passed}/{total} 测试通过")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 所有测试通过！系统运行正常。")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，请检查系统。")
        return 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

