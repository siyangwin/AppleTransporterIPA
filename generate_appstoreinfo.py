import os
import sys
import zipfile
import plistlib
from pathlib import Path

def extract_info_plist(ipa_path):
    """从IPA包中提取info.plist文件"""
    try:
        with zipfile.ZipFile(ipa_path, 'r') as ipa_zip:
            # 查找info.plist的路径（通常在Payload/应用名.app/Info.plist）
            info_plist_paths = [name for name in ipa_zip.namelist() 
                              if name.endswith('.app/Info.plist')]
            
            if not info_plist_paths:
                print("❌ 未在IPA包中找到Info.plist")
                return None
                
            # 提取第一个找到的Info.plist
            info_plist_path = info_plist_paths[0]
            with ipa_zip.open(info_plist_path) as f:
                # 解析plist内容
                return plistlib.load(f)
                
    except Exception as e:
        print(f"❌ 提取Info.plist失败: {str(e)}")
        return None

def generate_appstore_plist(ipa_path, output_path):
    """直接生成AppStoreInfo.plist的二进制版本（不依赖外部模板）"""
    # 1. 从IPA中提取info.plist
    print(f"正在从IPA中提取Info.plist: {ipa_path}")
    info_plist = extract_info_plist(ipa_path)
    if not info_plist:
        return False
    
    # 2. 提取必要的字段
    try:
        bundle_version = info_plist.get('CFBundleVersion', '')
        short_version = info_plist.get('CFBundleShortVersionString', '')
        bundle_id = info_plist.get('CFBundleIdentifier', '')
        
        if not all([bundle_version, short_version, bundle_id]):
            print("❌ 无法从Info.plist中获取必要的字段")
            print(f"  应用版本号: {short_version}")
            print(f"  构建版本号: {bundle_version}")
            print(f"  包名: {bundle_id}")
            return False
            
        print(f"提取的信息:")
        print(f"  应用版本号: {short_version}")
        print(f"  构建版本号: {bundle_version}")
        print(f"  包名: {bundle_id}")
        
    except Exception as e:
        print(f"❌ 解析Info.plist字段失败: {str(e)}")
        return False
    
    # 3. 直接构建AppStoreInfo.plist的结构
    try:
        # 构建完整的plist字典结构
        appstore_plist = {
            'product-metadata': {
                'packages': [
                    {
                        'bundles': [
                            {
                                'CFBundleShortVersionString': short_version,
                                'CFBundleVersion': bundle_version,
                                'Info.plist': {
                                    'content': info_plist  # 直接嵌入完整的info.plist内容
                                },
                                'bundle-identifier': bundle_id,
                                'platform-display-name': 'iOS App'
                            }
                        ]
                    }
                ]
            }
        }
        
        # 4. 保存为二进制plist
        with open(output_path, 'wb') as f:
            plistlib.dump(appstore_plist, f, fmt=plistlib.FMT_BINARY)
        
        print(f"✅ 成功生成二进制AppStoreInfo.plist: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ 生成AppStoreInfo.plist失败: {str(e)}")
        return False

def main():
    if len(sys.argv) != 3:
        print("用法: python generate_appstoreinfo_direct.py <IPA文件路径> <输出二进制plist路径>")
        print("示例: python generate_appstoreinfo_direct.py app.ipa AppStoreInfo.plist")
        sys.exit(1)
    
    ipa_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    
    # 验证输入文件是否存在
    if not ipa_path.exists():
        print(f"❌ IPA文件不存在: {ipa_path}")
        sys.exit(1)
    
    # 生成AppStoreInfo.plist
    success = generate_appstore_plist(ipa_path, output_path)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()