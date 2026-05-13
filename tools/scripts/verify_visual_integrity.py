#!/usr/bin/env python3
import sys
import subprocess
import os
from pathlib import Path

def verify_visual(xlsm_path):
    p = Path(xlsm_path)
    if not p.exists():
        return False, "檔案不存在"
    
    pdf_path = p.with_suffix(".pdf")
    try:
        # 使用 LibreOffice 將 xlsm 轉為 pdf 作為渲染測試
        res = subprocess.run([
            "libreoffice", "--headless", "--convert-to", "pdf",
            "--outdir", str(p.parent), str(p)
        ], capture_output=True, timeout=30)
        
        if res.returncode == 0 and pdf_path.exists():
            # 基本檢查：如果 PDF 大小大於 10KB，視為渲染成功
            size = pdf_path.stat().st_size
            if size > 10240:
                return True, f"視覺驗證通過 (PDF: {size} bytes)"
            else:
                return False, "渲染結果異常 (PDF 過小)"
        else:
            return False, f"LibreOffice 轉換失敗: {res.stderr.decode()}"
    except Exception as e:
        return False, f"驗證過程出錯: {e}"
    finally:
        if pdf_path.exists():
            pdf_path.unlink() # 刪除暫存檔

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    ok, msg = verify_visual(sys.argv[1])
    print(msg)
    sys.exit(0 if ok else 1)
