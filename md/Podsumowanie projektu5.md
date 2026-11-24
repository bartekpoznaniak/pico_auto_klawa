# Podsumowanie sesji — Pico HID, auto-repeat przycisków

## Stan wyjściowy

Projekt **Pico HID** działa na Raspberry Pi Pico z MicroPythonem i realizuje urządzenie HID: klawiaturę, mysz absolutną oraz interfejs na OLED 128x64 pod I2C. Urządzenie pozwala uruchamiać makra z katalogu `/scripts`, zarządzać harmonogramem zapisanym w `/schedules/harmonogram.txt`, wybudzać komputer przez klawisz `SHIFT` oraz wykonywać zaplanowane makro po wybudzeniu.[code.py](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/157352839/fc83ea8e-a0f0-407e-9d65-337a5492159d/code.py?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Checksum-Mode=ENABLED&X-Amz-Credential=ASIA2F3EMEYEYIWZKYM7%2F20261123%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20261123T163439Z&X-Amz-Expires=3245&X-Amz-Security-Token=IQoJb3JpZ2luX2VjELH%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJGMEQCIB%2FZ46iOp8GIqXKE8gQH6dKQQNt776ppylhM0CCgugyxAiBrmhnDjc7NCA3hxCOQ7ws%2FhDBymKM%2B6Zza7p8NULdFeyqABQh6EAEaDDY5OTc1MzMwOTcwNSIMLi%2BJ6cClgDGaxDlCKt0EB4cEPEevk2CfDpzFwYi2%2FJPRMsLWQlirMa7J58H2Ff9TRsOcpMj1Fe8XEygXAPAmDbXuGKtGp7ebgeNUS%2FmKx%2BpwvFQgCRAZXB8YcniYma6yjx5EZ3lbE81dsz5p2RZX3FqjFhGcTpS13LUjF2jd1SbyJb5TDdtHVwnqbvvzUxQ56dAcQqq0gKKqJqwMv39iu8G%2FwxoWodqz%2FtHDVAfDX7FMjVlA55WpqDswlVF8jf1BSJ%2BaXE8ORQSeBuDAFXLdXebBjPR5JfvpSCiZ5kcpsgoZ1EIESvi7nI2tWItk2ZMpuAHLKJZWr06RL6I%2BN3uCDNG6R4WY%2FUJMYCysUeIazPFR9fqvCJWC9gojA%2BgNxYMGguHBsUkXyAIwGN2MMsve1yMxYgk3O8M%2FceB4oEuZd29bQEPoVTIGC0oEWqKorVlN7ha8m4kJSvBtG0m%2FKw1KD6HLKkz0901DzonVCVjIkz9d79JaGIP1U3hDSojyYrm4gbRtOJ0Bfi2JRUHyJq3CaiJNmxPNQQjIIIYn4C%2FXnfURISGWjDcMfZYAW5lb3VCnp9%2BmjC1UxVHcItpUZyfvuESKLMK3guK5DwAeJfeYcAvB1FW5ohIgcxELYmfhkOAeDOtihQ9eNH5V%2FP8tO5a3K7RosVfVfTUvwtAF3ZaV6uMRwYa5ukthpNXtmtpkOVh2aEKaKoqVBPPEN7zgXR3Dsq3hNq%2FxuKWT%2Bt%2Bg9zkG1utMa2BoNn%2FFS36sumbvIISeqq4dbQF6Pz%2BjhXD%2BLGEC733CGQxbNhHeFKUeRWRmnol%2FJe3kr5gva%2FV1HZkw%2BdOR2AY6mQFx%2BCSNAyF%2FUw6YipM0tdywkP7cTtVbmr%2Fjl7AYz7re5CrBW3DksZCEeeFxD1mcu1Kfiuwb5ekvtpItdTZFqrDdQgAY11DCDlxqH%2Fhg0xiTfG4mjgQ6rFwxs3gNUsWAXSty%2Bv1dSP18yjX361ciIizaicJV8csCz9BZoeCAQZxANYwyF4fZmaexial4E7v7dx54Zp0FAYtNwog%3D&X-Amz-SignedHeaders=host&x-id=GetObject&X-Amz-Signature=f996fc16b9cda276679d78a987a36ac01a779057a5ec4b0ee864ff857df76e3b)

Wersja kodu na początku sesji to `1.242`, a po zmianach `1.243d`. Główne pliki to `boot.py`, `code.py` i `scriptengine.py`.[code.py](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/157352839/fc83ea8e-a0f0-407e-9d65-337a5492159d/code.py?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Checksum-Mode=ENABLED&X-Amz-Credential=ASIA2F3EMEYEYIWZKYM7%2F20261123%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20261123T163439Z&X-Amz-Expires=3245&X-Amz-Security-Token=IQoJb3JpZ2luX2VjELH%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJGMEQCIB%2FZ46iOp8GIqXKE8gQH6dKQQNt776ppylhM0CCgugyxAiBrmhnDjc7NCA3hxCOQ7ws%2FhDBymKM%2B6Zza7p8NULdFeyqABQh6EAEaDDY5OTc1MzMwOTcwNSIMLi%2BJ6cClgDGaxDlCKt0EB4cEPEevk2CfDpzFwYi2%2FJPRMsLWQlirMa7J58H2Ff9TRsOcpMj1Fe8XEygXAPAmDbXuGKtGp7ebgeNUS%2FmKx%2BpwvFQgCRAZXB8YcniYma6yjx5EZ3lbE81dsz5p2RZX3FqjFhGcTpS13LUjF2jd1SbyJb5TDdtHVwnqbvvzUxQ56dAcQqq0gKKqJqwMv39iu8G%2FwxoWodqz%2FtHDVAfDX7FMjVlA55WpqDswlVF8jf1BSJ%2BaXE8ORQSeBuDAFXLdXebBjPR5JfvpSCiZ5kcpsgoZ1EIESvi7nI2tWItk2ZMpuAHLKJZWr06RL6I%2BN3uCDNG6R4WY%2FUJMYCysUeIazPFR9fqvCJWC9gojA%2BgNxYMGguHBsUkXyAIwGN2MMsve1yMxYgk3O8M%2FceB4oEuZd29bQEPoVTIGC0oEWqKorVlN7ha8m4kJSvBtG0m%2FKw1KD6HLKkz0901DzonVCVjIkz9d79JaGIP1U3hDSojyYrm4gbRtOJ0Bfi2JRUHyJq3CaiJNmxPNQQjIIIYn4C%2FXnfURISGWjDcMfZYAW5lb3VCnp9%2BmjC1UxVHcItpUZyfvuESKLMK3guK5DwAeJfeYcAvB1FW5ohIgcxELYmfhkOAeDOtihQ9eNH5V%2FP8tO5a3K7RosVfVfTUvwtAF3ZaV6uMRwYa5ukthpNXtmtpkOVh2aEKaKoqVBPPEN7zgXR3Dsq3hNq%2FxuKWT%2Bt%2Bg9zkG1utMa2BoNn%2FFS36sumbvIISeqq4dbQF6Pz%2BjhXD%2BLGEC733CGQxbNhHeFKUeRWRmnol%2FJe3kr5gva%2FV1HZkw%2BdOR2AY6mQFx%2BCSNAyF%2FUw6YipM0tdywkP7cTtVbmr%2Fjl7AYz7re5CrBW3DksZCEeeFxD1mcu1Kfiuwb5ekvtpItdTZFqrDdQgAY11DCDlxqH%2Fhg0xiTfG4mjgQ6rFwxs3gNUsWAXSty%2Bv1dSP18yjX361ciIizaicJV8csCz9BZoeCAQZxANYwyF4fZmaexial4E7v7dx54Zp0FAYtNwog%3D&X-Amz-SignedHeaders=host&x-id=GetObject&X-Amz-Signature=f996fc16b9cda276679d78a987a36ac01a779057a5ec4b0ee864ff857df76e3b)

## Sprzęt i architektura

- Przycisk 1: `GP14`, aktywny stan niski, pull-up.

- Przycisk 2: `GP15`, aktywny stan niski, pull-up.

- OLED: SSD1306 128x64, I2C, `SCL=GP5`, `SDA=GP4`, adres `0x3C`.

- LED: wbudowany `board.LED`.

- USB HID: klawiatura oraz mysz absolutna, Report ID 7.

- USB CDC: konsola Thonny oraz osobny kanał danych.[code.py](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/157352839/fc83ea8e-a0f0-407e-9d65-337a5492159d/code.py?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Checksum-Mode=ENABLED&X-Amz-Credential=ASIA2F3EMEYEYIWZKYM7%2F20261123%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20261123T163439Z&X-Amz-Expires=3245&X-Amz-Security-Token=IQoJb3JpZ2luX2VjELH%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJGMEQCIB%2FZ46iOp8GIqXKE8gQH6dKQQNt776ppylhM0CCgugyxAiBrmhnDjc7NCA3hxCOQ7ws%2FhDBymKM%2B6Zza7p8NULdFeyqABQh6EAEaDDY5OTc1MzMwOTcwNSIMLi%2BJ6cClgDGaxDlCKt0EB4cEPEevk2CfDpzFwYi2%2FJPRMsLWQlirMa7J58H2Ff9TRsOcpMj1Fe8XEygXAPAmDbXuGKtGp7ebgeNUS%2FmKx%2BpwvFQgCRAZXB8YcniYma6yjx5EZ3lbE81dsz5p2RZX3FqjFhGcTpS13LUjF2jd1SbyJb5TDdtHVwnqbvvzUxQ56dAcQqq0gKKqJqwMv39iu8G%2FwxoWodqz%2FtHDVAfDX7FMjVlA55WpqDswlVF8jf1BSJ%2BaXE8ORQSeBuDAFXLdXebBjPR5JfvpSCiZ5kcpsgoZ1EIESvi7nI2tWItk2ZMpuAHLKJZWr06RL6I%2BN3uCDNG6R4WY%2FUJMYCysUeIazPFR9fqvCJWC9gojA%2BgNxYMGguHBsUkXyAIwGN2MMsve1yMxYgk3O8M%2FceB4oEuZd29bQEPoVTIGC0oEWqKorVlN7ha8m4kJSvBtG0m%2FKw1KD6HLKkz0901DzonVCVjIkz9d79JaGIP1U3hDSojyYrm4gbRtOJ0Bfi2JRUHyJq3CaiJNmxPNQQjIIIYn4C%2FXnfURISGWjDcMfZYAW5lb3VCnp9%2BmjC1UxVHcItpUZyfvuESKLMK3guK5DwAeJfeYcAvB1FW5ohIgcxELYmfhkOAeDOtihQ9eNH5V%2FP8tO5a3K7RosVfVfTUvwtAF3ZaV6uMRwYa5ukthpNXtmtpkOVh2aEKaKoqVBPPEN7zgXR3Dsq3hNq%2FxuKWT%2Bt%2Bg9zkG1utMa2BoNn%2FFS36sumbvIISeqq4dbQF6Pz%2BjhXD%2BLGEC733CGQxbNhHeFKUeRWRmnol%2FJe3kr5gva%2FV1HZkw%2BdOR2AY6mQFx%2BCSNAyF%2FUw6YipM0tdywkP7cTtVbmr%2Fjl7AYz7re5CrBW3DksZCEeeFxD1mcu1Kfiuwb5ekvtpItdTZFqrDdQgAY11DCDlxqH%2Fhg0xiTfG4mjgQ6rFwxs3gNUsWAXSty%2Bv1dSP18yjX361ciIizaicJV8csCz9BZoeCAQZxANYwyF4fZmaexial4E7v7dx54Zp0FAYtNwog%3D&X-Amz-SignedHeaders=host&x-id=GetObject&X-Amz-Signature=f996fc16b9cda276679d78a987a36ac01a779057a5ec4b0ee864ff857df76e3b)

`boot.py` pozwala na zapis systemu plików z Windows tylko wtedy, gdy podczas resetu lub podłączenia USB przytrzymany jest `GP15`. Bez tego system plików jest montowany tylko do odczytu.

## Cel dzisiejszej zmiany

Celem było dodanie **auto-repeat**, czyli automatycznego powtarzania akcji podczas przytrzymania przycisku. Miało to dotyczyć:

- zwiększania godzin na ekranie `edit_hour`,

- zwiększania minut na ekranie `edit_minute`,

- przewijania listy makr na ekranie `scripts`,

- przewijania wpisów harmonogramu na ekranie `harmonogram`,

- przewijania opcji planu na ekranie `schedule_active`.[code.py](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/157352839/fc83ea8e-a0f0-407e-9d65-337a5492159d/code.py?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Checksum-Mode=ENABLED&X-Amz-Credential=ASIA2F3EMEYEYIWZKYM7%2F20261123%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20261123T163439Z&X-Amz-Expires=3245&X-Amz-Security-Token=IQoJb3JpZ2luX2VjELH%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJGMEQCIB%2FZ46iOp8GIqXKE8gQH6dKQQNt776ppylhM0CCgugyxAiBrmhnDjc7NCA3hxCOQ7ws%2FhDBymKM%2B6Zza7p8NULdFeyqABQh6EAEaDDY5OTc1MzMwOTcwNSIMLi%2BJ6cClgDGaxDlCKt0EB4cEPEevk2CfDpzFwYi2%2FJPRMsLWQlirMa7J58H2Ff9TRsOcpMj1Fe8XEygXAPAmDbXuGKtGp7ebgeNUS%2FmKx%2BpwvFQgCRAZXB8YcniYma6yjx5EZ3lbE81dsz5p2RZX3FqjFhGcTpS13LUjF2jd1SbyJb5TDdtHVwnqbvvzUxQ56dAcQqq0gKKqJqwMv39iu8G%2FwxoWodqz%2FtHDVAfDX7FMjVlA55WpqDswlVF8jf1BSJ%2BaXE8ORQSeBuDAFXLdXebBjPR5JfvpSCiZ5kcpsgoZ1EIESvi7nI2tWItk2ZMpuAHLKJZWr06RL6I%2BN3uCDNG6R4WY%2FUJMYCysUeIazPFR9fqvCJWC9gojA%2BgNxYMGguHBsUkXyAIwGN2MMsve1yMxYgk3O8M%2FceB4oEuZd29bQEPoVTIGC0oEWqKorVlN7ha8m4kJSvBtG0m%2FKw1KD6HLKkz0901DzonVCVjIkz9d79JaGIP1U3hDSojyYrm4gbRtOJ0Bfi2JRUHyJq3CaiJNmxPNQQjIIIYn4C%2FXnfURISGWjDcMfZYAW5lb3VCnp9%2BmjC1UxVHcItpUZyfvuESKLMK3guK5DwAeJfeYcAvB1FW5ohIgcxELYmfhkOAeDOtihQ9eNH5V%2FP8tO5a3K7RosVfVfTUvwtAF3ZaV6uMRwYa5ukthpNXtmtpkOVh2aEKaKoqVBPPEN7zgXR3Dsq3hNq%2FxuKWT%2Bt%2Bg9zkG1utMa2BoNn%2FFS36sumbvIISeqq4dbQF6Pz%2BjhXD%2BLGEC733CGQxbNhHeFKUeRWRmnol%2FJe3kr5gva%2FV1HZkw%2BdOR2AY6mQFx%2BCSNAyF%2FUw6YipM0tdywkP7cTtVbmr%2Fjl7AYz7re5CrBW3DksZCEeeFxD1mcu1Kfiuwb5ekvtpItdTZFqrDdQgAY11DCDlxqH%2Fhg0xiTfG4mjgQ6rFwxs3gNUsWAXSty%2Bv1dSP18yjX361ciIizaicJV8csCz9BZoeCAQZxANYwyF4fZmaexial4E7v7dx54Zp0FAYtNwog%3D&X-Amz-SignedHeaders=host&x-id=GetObject&X-Amz-Signature=f996fc16b9cda276679d78a987a36ac01a779057a5ec4b0ee864ff857df76e3b)

Zamierzone zachowanie: krótkie kliknięcie wykonuje jeden krok, a przytrzymanie najpierw czeka, po czym zaczyna powtarzać akcję coraz szybciej.[code.py](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/157352839/fc83ea8e-a0f0-407e-9d65-337a5492159d/code.py?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Checksum-Mode=ENABLED&X-Amz-Credential=ASIA2F3EMEYEYIWZKYM7%2F20261123%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20261123T163439Z&X-Amz-Expires=3245&X-Amz-Security-Token=IQoJb3JpZ2luX2VjELH%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJGMEQCIB%2FZ46iOp8GIqXKE8gQH6dKQQNt776ppylhM0CCgugyxAiBrmhnDjc7NCA3hxCOQ7ws%2FhDBymKM%2B6Zza7p8NULdFeyqABQh6EAEaDDY5OTc1MzMwOTcwNSIMLi%2BJ6cClgDGaxDlCKt0EB4cEPEevk2CfDpzFwYi2%2FJPRMsLWQlirMa7J58H2Ff9TRsOcpMj1Fe8XEygXAPAmDbXuGKtGp7ebgeNUS%2FmKx%2BpwvFQgCRAZXB8YcniYma6yjx5EZ3lbE81dsz5p2RZX3FqjFhGcTpS13LUjF2jd1SbyJb5TDdtHVwnqbvvzUxQ56dAcQqq0gKKqJqwMv39iu8G%2FwxoWodqz%2FtHDVAfDX7FMjVlA55WpqDswlVF8jf1BSJ%2BaXE8ORQSeBuDAFXLdXebBjPR5JfvpSCiZ5kcpsgoZ1EIESvi7nI2tWItk2ZMpuAHLKJZWr06RL6I%2BN3uCDNG6R4WY%2FUJMYCysUeIazPFR9fqvCJWC9gojA%2BgNxYMGguHBsUkXyAIwGN2MMsve1yMxYgk3O8M%2FceB4oEuZd29bQEPoVTIGC0oEWqKorVlN7ha8m4kJSvBtG0m%2FKw1KD6HLKkz0901DzonVCVjIkz9d79JaGIP1U3hDSojyYrm4gbRtOJ0Bfi2JRUHyJq3CaiJNmxPNQQjIIIYn4C%2FXnfURISGWjDcMfZYAW5lb3VCnp9%2BmjC1UxVHcItpUZyfvuESKLMK3guK5DwAeJfeYcAvB1FW5ohIgcxELYmfhkOAeDOtihQ9eNH5V%2FP8tO5a3K7RosVfVfTUvwtAF3ZaV6uMRwYa5ukthpNXtmtpkOVh2aEKaKoqVBPPEN7zgXR3Dsq3hNq%2FxuKWT%2Bt%2Bg9zkG1utMa2BoNn%2FFS36sumbvIISeqq4dbQF6Pz%2BjhXD%2BLGEC733CGQxbNhHeFKUeRWRmnol%2FJe3kr5gva%2FV1HZkw%2BdOR2AY6mQFx%2BCSNAyF%2FUw6YipM0tdywkP7cTtVbmr%2Fjl7AYz7re5CrBW3DksZCEeeFxD1mcu1Kfiuwb5ekvtpItdTZFqrDdQgAY11DCDlxqH%2Fhg0xiTfG4mjgQ6rFwxs3gNUsWAXSty%2Bv1dSP18yjX361ciIizaicJV8csCz9BZoeCAQZxANYwyF4fZmaexial4E7v7dx54Zp0FAYtNwog%3D&X-Amz-SignedHeaders=host&x-id=GetObject&X-Amz-Signature=f996fc16b9cda276679d78a987a36ac01a779057a5ec4b0ee864ff857df76e3b)

## Dodana funkcja auto-repeat

Do `code.py` dodano funkcję:

python

`def auto_repeat(pressed, previous, last_time, delay):     now = time.monotonic()     if not pressed:         return False, now, 0.45     if not previous:         return True, now, 0.45     if now - last_time >= delay:         next_delay = max(0.08, delay * 0.7)         return True, now, next_delay     return False, last_time, delay`

Parametry regulujące:

- `0.45` — czas od pierwszego wciśnięcia do startu powtarzania.

- `0.08` — minimalny, najszybszy odstęp między krokami.

- `delay * 0.7` — tempo przyspieszania po każdym kolejnym kroku.[code.py](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/157352839/fc83ea8e-a0f0-407e-9d65-337a5492159d/code.py?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Checksum-Mode=ENABLED&X-Amz-Credential=ASIA2F3EMEYEYIWZKYM7%2F20261123%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20261123T163439Z&X-Amz-Expires=3245&X-Amz-Security-Token=IQoJb3JpZ2luX2VjELH%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJGMEQCIB%2FZ46iOp8GIqXKE8gQH6dKQQNt776ppylhM0CCgugyxAiBrmhnDjc7NCA3hxCOQ7ws%2FhDBymKM%2B6Zza7p8NULdFeyqABQh6EAEaDDY5OTc1MzMwOTcwNSIMLi%2BJ6cClgDGaxDlCKt0EB4cEPEevk2CfDpzFwYi2%2FJPRMsLWQlirMa7J58H2Ff9TRsOcpMj1Fe8XEygXAPAmDbXuGKtGp7ebgeNUS%2FmKx%2BpwvFQgCRAZXB8YcniYma6yjx5EZ3lbE81dsz5p2RZX3FqjFhGcTpS13LUjF2jd1SbyJb5TDdtHVwnqbvvzUxQ56dAcQqq0gKKqJqwMv39iu8G%2FwxoWodqz%2FtHDVAfDX7FMjVlA55WpqDswlVF8jf1BSJ%2BaXE8ORQSeBuDAFXLdXebBjPR5JfvpSCiZ5kcpsgoZ1EIESvi7nI2tWItk2ZMpuAHLKJZWr06RL6I%2BN3uCDNG6R4WY%2FUJMYCysUeIazPFR9fqvCJWC9gojA%2BgNxYMGguHBsUkXyAIwGN2MMsve1yMxYgk3O8M%2FceB4oEuZd29bQEPoVTIGC0oEWqKorVlN7ha8m4kJSvBtG0m%2FKw1KD6HLKkz0901DzonVCVjIkz9d79JaGIP1U3hDSojyYrm4gbRtOJ0Bfi2JRUHyJq3CaiJNmxPNQQjIIIYn4C%2FXnfURISGWjDcMfZYAW5lb3VCnp9%2BmjC1UxVHcItpUZyfvuESKLMK3guK5DwAeJfeYcAvB1FW5ohIgcxELYmfhkOAeDOtihQ9eNH5V%2FP8tO5a3K7RosVfVfTUvwtAF3ZaV6uMRwYa5ukthpNXtmtpkOVh2aEKaKoqVBPPEN7zgXR3Dsq3hNq%2FxuKWT%2Bt%2Bg9zkG1utMa2BoNn%2FFS36sumbvIISeqq4dbQF6Pz%2BjhXD%2BLGEC733CGQxbNhHeFKUeRWRmnol%2FJe3kr5gva%2FV1HZkw%2BdOR2AY6mQFx%2BCSNAyF%2FUw6YipM0tdywkP7cTtVbmr%2Fjl7AYz7re5CrBW3DksZCEeeFxD1mcu1Kfiuwb5ekvtpItdTZFqrDdQgAY11DCDlxqH%2Fhg0xiTfG4mjgQ6rFwxs3gNUsWAXSty%2Bv1dSP18yjX361ciIizaicJV8csCz9BZoeCAQZxANYwyF4fZmaexial4E7v7dx54Zp0FAYtNwog%3D&X-Amz-SignedHeaders=host&x-id=GetObject&X-Amz-Signature=f996fc16b9cda276679d78a987a36ac01a779057a5ec4b0ee864ff857df76e3b)

W głównej pętli dodano zmienne:

python

`last14 = 0.0 delay14 = 0.45 last15 = 0.0 delay15 = 0.45`

oraz wywołania:

python

`step14, last14, delay14 = auto_repeat(     pressed14, previous14, last14, delay14 ) step15, last15, delay15 = auto_repeat(     pressed15, previous15, last15, delay15 )`

Przy jednoczesnym wciśnięciu `GP14` i `GP15` oba kroki są wyłączane, ponieważ ten zestaw służy do wejścia do menu.[code.py](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/157352839/fc83ea8e-a0f0-407e-9d65-337a5492159d/code.py?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Checksum-Mode=ENABLED&X-Amz-Credential=ASIA2F3EMEYEYIWZKYM7%2F20261123%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20261123T163439Z&X-Amz-Expires=3245&X-Amz-Security-Token=IQoJb3JpZ2luX2VjELH%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJGMEQCIB%2FZ46iOp8GIqXKE8gQH6dKQQNt776ppylhM0CCgugyxAiBrmhnDjc7NCA3hxCOQ7ws%2FhDBymKM%2B6Zza7p8NULdFeyqABQh6EAEaDDY5OTc1MzMwOTcwNSIMLi%2BJ6cClgDGaxDlCKt0EB4cEPEevk2CfDpzFwYi2%2FJPRMsLWQlirMa7J58H2Ff9TRsOcpMj1Fe8XEygXAPAmDbXuGKtGp7ebgeNUS%2FmKx%2BpwvFQgCRAZXB8YcniYma6yjx5EZ3lbE81dsz5p2RZX3FqjFhGcTpS13LUjF2jd1SbyJb5TDdtHVwnqbvvzUxQ56dAcQqq0gKKqJqwMv39iu8G%2FwxoWodqz%2FtHDVAfDX7FMjVlA55WpqDswlVF8jf1BSJ%2BaXE8ORQSeBuDAFXLdXebBjPR5JfvpSCiZ5kcpsgoZ1EIESvi7nI2tWItk2ZMpuAHLKJZWr06RL6I%2BN3uCDNG6R4WY%2FUJMYCysUeIazPFR9fqvCJWC9gojA%2BgNxYMGguHBsUkXyAIwGN2MMsve1yMxYgk3O8M%2FceB4oEuZd29bQEPoVTIGC0oEWqKorVlN7ha8m4kJSvBtG0m%2FKw1KD6HLKkz0901DzonVCVjIkz9d79JaGIP1U3hDSojyYrm4gbRtOJ0Bfi2JRUHyJq3CaiJNmxPNQQjIIIYn4C%2FXnfURISGWjDcMfZYAW5lb3VCnp9%2BmjC1UxVHcItpUZyfvuESKLMK3guK5DwAeJfeYcAvB1FW5ohIgcxELYmfhkOAeDOtihQ9eNH5V%2FP8tO5a3K7RosVfVfTUvwtAF3ZaV6uMRwYa5ukthpNXtmtpkOVh2aEKaKoqVBPPEN7zgXR3Dsq3hNq%2FxuKWT%2Bt%2Bg9zkG1utMa2BoNn%2FFS36sumbvIISeqq4dbQF6Pz%2BjhXD%2BLGEC733CGQxbNhHeFKUeRWRmnol%2FJe3kr5gva%2FV1HZkw%2BdOR2AY6mQFx%2BCSNAyF%2FUw6YipM0tdywkP7cTtVbmr%2Fjl7AYz7re5CrBW3DksZCEeeFxD1mcu1Kfiuwb5ekvtpItdTZFqrDdQgAY11DCDlxqH%2Fhg0xiTfG4mjgQ6rFwxs3gNUsWAXSty%2Bv1dSP18yjX361ciIizaicJV8csCz9BZoeCAQZxANYwyF4fZmaexial4E7v7dx54Zp0FAYtNwog%3D&X-Amz-SignedHeaders=host&x-id=GetObject&X-Amz-Signature=f996fc16b9cda276679d78a987a36ac01a779057a5ec4b0ee864ff857df76e3b)

## Zmiany w ekranach

W ekranie `edit_hour` zmieniono:

python

`if step14:     edit_hour = (edit_hour + 1) % 24     update_display()     last_refresh = time.monotonic() elif released15:     screen = "edit_minute"`

W ekranie `edit_minute` zmieniono:

python

`if step14:     edit_minute = (edit_minute + 1) % 60     update_display()     last_refresh = time.monotonic() elif released15:     ...`

W liście makr `scripts` zmieniono:

python

`if step15:     script_index = (script_index + 1) % len(script_names)     update_display()     last_refresh = time.monotonic() elif released14:     ...`

W harmonogramie `harmonogram` zmieniono:

python

`if step15:     schedule_index = (schedule_index + 1) % len(schedule_entries)     update_display()     last_refresh = time.monotonic() elif released14:     ...`

W opcjach aktywnego planu `schedule_active` zmieniono:

python

`if step15:     plan_action_index = (plan_action_index + 1) % len(plan_actions)     update_display()     last_refresh = time.monotonic() elif released14:     ...`

Zatwierdzenia, wejścia do kolejnych ekranów, zapis harmonogramu i uruchamianie makr nadal mają działać na `released14` albo `released15`, czyli po krótkim kliknięciu.[code.py](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/157352839/fc83ea8e-a0f0-407e-9d65-337a5492159d/code.py?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Checksum-Mode=ENABLED&X-Amz-Credential=ASIA2F3EMEYEYIWZKYM7%2F20261123%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20261123T163439Z&X-Amz-Expires=3245&X-Amz-Security-Token=IQoJb3JpZ2luX2VjELH%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJGMEQCIB%2FZ46iOp8GIqXKE8gQH6dKQQNt776ppylhM0CCgugyxAiBrmhnDjc7NCA3hxCOQ7ws%2FhDBymKM%2B6Zza7p8NULdFeyqABQh6EAEaDDY5OTc1MzMwOTcwNSIMLi%2BJ6cClgDGaxDlCKt0EB4cEPEevk2CfDpzFwYi2%2FJPRMsLWQlirMa7J58H2Ff9TRsOcpMj1Fe8XEygXAPAmDbXuGKtGp7ebgeNUS%2FmKx%2BpwvFQgCRAZXB8YcniYma6yjx5EZ3lbE81dsz5p2RZX3FqjFhGcTpS13LUjF2jd1SbyJb5TDdtHVwnqbvvzUxQ56dAcQqq0gKKqJqwMv39iu8G%2FwxoWodqz%2FtHDVAfDX7FMjVlA55WpqDswlVF8jf1BSJ%2BaXE8ORQSeBuDAFXLdXebBjPR5JfvpSCiZ5kcpsgoZ1EIESvi7nI2tWItk2ZMpuAHLKJZWr06RL6I%2BN3uCDNG6R4WY%2FUJMYCysUeIazPFR9fqvCJWC9gojA%2BgNxYMGguHBsUkXyAIwGN2MMsve1yMxYgk3O8M%2FceB4oEuZd29bQEPoVTIGC0oEWqKorVlN7ha8m4kJSvBtG0m%2FKw1KD6HLKkz0901DzonVCVjIkz9d79JaGIP1U3hDSojyYrm4gbRtOJ0Bfi2JRUHyJq3CaiJNmxPNQQjIIIYn4C%2FXnfURISGWjDcMfZYAW5lb3VCnp9%2BmjC1UxVHcItpUZyfvuESKLMK3guK5DwAeJfeYcAvB1FW5ohIgcxELYmfhkOAeDOtihQ9eNH5V%2FP8tO5a3K7RosVfVfTUvwtAF3ZaV6uMRwYa5ukthpNXtmtpkOVh2aEKaKoqVBPPEN7zgXR3Dsq3hNq%2FxuKWT%2Bt%2Bg9zkG1utMa2BoNn%2FFS36sumbvIISeqq4dbQF6Pz%2BjhXD%2BLGEC733CGQxbNhHeFKUeRWRmnol%2FJe3kr5gva%2FV1HZkw%2BdOR2AY6mQFx%2BCSNAyF%2FUw6YipM0tdywkP7cTtVbmr%2Fjl7AYz7re5CrBW3DksZCEeeFxD1mcu1Kfiuwb5ekvtpItdTZFqrDdQgAY11DCDlxqH%2Fhg0xiTfG4mjgQ6rFwxs3gNUsWAXSty%2Bv1dSP18yjX361ciIizaicJV8csCz9BZoeCAQZxANYwyF4fZmaexial4E7v7dx54Zp0FAYtNwog%3D&X-Amz-SignedHeaders=host&x-id=GetObject&X-Amz-Signature=f996fc16b9cda276679d78a987a36ac01a779057a5ec4b0ee864ff857df76e3b)

## Diagnostyka konsolowa

Dodano print diagnostyczny w głównej pętli:

python

`print(     "BTN14={} BTN15={} STEP14={} STEP15={} "     "D14={:.2f} D15={:.2f}".format(         pressed14, pressed15,         step14, step15,         delay14, delay15    ) )`

Test wykazał, że przy przytrzymaniu `GP14` pojawiają się cyklicznie:

text

`BTN14=True BTN15=False STEP14=True STEP15=False D14=0.08 D15=0.45 BTN14=True BTN15=False STEP14=False STEP15=False D14=0.08 D15=0.45 BTN14=True BTN15=False STEP14=False STEP15=False D14=0.08 D15=0.45 BTN14=True BTN15=False STEP14=True STEP15=False D14=0.08 D15=0.45`

Oznacza to, że sama funkcja `auto_repeat()` działa poprawnie: `STEP14=True` pojawia się co około 80 ms.[code.py](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/157352839/fc83ea8e-a0f0-407e-9d65-337a5492159d/code.py?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Checksum-Mode=ENABLED&X-Amz-Credential=ASIA2F3EMEYEYIWZKYM7%2F20261123%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20261123T163439Z&X-Amz-Expires=3245&X-Amz-Security-Token=IQoJb3JpZ2luX2VjELH%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJGMEQCIB%2FZ46iOp8GIqXKE8gQH6dKQQNt776ppylhM0CCgugyxAiBrmhnDjc7NCA3hxCOQ7ws%2FhDBymKM%2B6Zza7p8NULdFeyqABQh6EAEaDDY5OTc1MzMwOTcwNSIMLi%2BJ6cClgDGaxDlCKt0EB4cEPEevk2CfDpzFwYi2%2FJPRMsLWQlirMa7J58H2Ff9TRsOcpMj1Fe8XEygXAPAmDbXuGKtGp7ebgeNUS%2FmKx%2BpwvFQgCRAZXB8YcniYma6yjx5EZ3lbE81dsz5p2RZX3FqjFhGcTpS13LUjF2jd1SbyJb5TDdtHVwnqbvvzUxQ56dAcQqq0gKKqJqwMv39iu8G%2FwxoWodqz%2FtHDVAfDX7FMjVlA55WpqDswlVF8jf1BSJ%2BaXE8ORQSeBuDAFXLdXebBjPR5JfvpSCiZ5kcpsgoZ1EIESvi7nI2tWItk2ZMpuAHLKJZWr06RL6I%2BN3uCDNG6R4WY%2FUJMYCysUeIazPFR9fqvCJWC9gojA%2BgNxYMGguHBsUkXyAIwGN2MMsve1yMxYgk3O8M%2FceB4oEuZd29bQEPoVTIGC0oEWqKorVlN7ha8m4kJSvBtG0m%2FKw1KD6HLKkz0901DzonVCVjIkz9d79JaGIP1U3hDSojyYrm4gbRtOJ0Bfi2JRUHyJq3CaiJNmxPNQQjIIIYn4C%2FXnfURISGWjDcMfZYAW5lb3VCnp9%2BmjC1UxVHcItpUZyfvuESKLMK3guK5DwAeJfeYcAvB1FW5ohIgcxELYmfhkOAeDOtihQ9eNH5V%2FP8tO5a3K7RosVfVfTUvwtAF3ZaV6uMRwYa5ukthpNXtmtpkOVh2aEKaKoqVBPPEN7zgXR3Dsq3hNq%2FxuKWT%2Bt%2Bg9zkG1utMa2BoNn%2FFS36sumbvIISeqq4dbQF6Pz%2BjhXD%2BLGEC733CGQxbNhHeFKUeRWRmnol%2FJe3kr5gva%2FV1HZkw%2BdOR2AY6mQFx%2BCSNAyF%2FUw6YipM0tdywkP7cTtVbmr%2Fjl7AYz7re5CrBW3DksZCEeeFxD1mcu1Kfiuwb5ekvtpItdTZFqrDdQgAY11DCDlxqH%2Fhg0xiTfG4mjgQ6rFwxs3gNUsWAXSty%2Bv1dSP18yjX361ciIizaicJV8csCz9BZoeCAQZxANYwyF4fZmaexial4E7v7dx54Zp0FAYtNwog%3D&X-Amz-SignedHeaders=host&x-id=GetObject&X-Amz-Signature=f996fc16b9cda276679d78a987a36ac01a779057a5ec4b0ee864ff857df76e3b)

## Znaleziony główny problem

Mimo poprawnego `STEP14=True` godzina i minuta nie rosły. Przyczyną jest **struktura obsługi przycisków**: cała obsługa ekranów, w tym `elif screen == "edit_hour":` i `elif screen == "edit_minute":`, znajduje się wewnątrz warunku:

python

`if (pressed14, pressed15) != (previous14, previous15):`

Ten warunek wykonuje kod tylko wtedy, gdy stan przycisków się zmienia. Podczas przytrzymania przycisku stan pozostaje ten sam, więc kod nie dochodzi do sekcji zwiększającej godzinę lub minutę.[code.py](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/157352839/fc83ea8e-a0f0-407e-9d65-337a5492159d/code.py?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Checksum-Mode=ENABLED&X-Amz-Credential=ASIA2F3EMEYEYIWZKYM7%2F20261123%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20261123T163439Z&X-Amz-Expires=3245&X-Amz-Security-Token=IQoJb3JpZ2luX2VjELH%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJGMEQCIB%2FZ46iOp8GIqXKE8gQH6dKQQNt776ppylhM0CCgugyxAiBrmhnDjc7NCA3hxCOQ7ws%2FhDBymKM%2B6Zza7p8NULdFeyqABQh6EAEaDDY5OTc1MzMwOTcwNSIMLi%2BJ6cClgDGaxDlCKt0EB4cEPEevk2CfDpzFwYi2%2FJPRMsLWQlirMa7J58H2Ff9TRsOcpMj1Fe8XEygXAPAmDbXuGKtGp7ebgeNUS%2FmKx%2BpwvFQgCRAZXB8YcniYma6yjx5EZ3lbE81dsz5p2RZX3FqjFhGcTpS13LUjF2jd1SbyJb5TDdtHVwnqbvvzUxQ56dAcQqq0gKKqJqwMv39iu8G%2FwxoWodqz%2FtHDVAfDX7FMjVlA55WpqDswlVF8jf1BSJ%2BaXE8ORQSeBuDAFXLdXebBjPR5JfvpSCiZ5kcpsgoZ1EIESvi7nI2tWItk2ZMpuAHLKJZWr06RL6I%2BN3uCDNG6R4WY%2FUJMYCysUeIazPFR9fqvCJWC9gojA%2BgNxYMGguHBsUkXyAIwGN2MMsve1yMxYgk3O8M%2FceB4oEuZd29bQEPoVTIGC0oEWqKorVlN7ha8m4kJSvBtG0m%2FKw1KD6HLKkz0901DzonVCVjIkz9d79JaGIP1U3hDSojyYrm4gbRtOJ0Bfi2JRUHyJq3CaiJNmxPNQQjIIIYn4C%2FXnfURISGWjDcMfZYAW5lb3VCnp9%2BmjC1UxVHcItpUZyfvuESKLMK3guK5DwAeJfeYcAvB1FW5ohIgcxELYmfhkOAeDOtihQ9eNH5V%2FP8tO5a3K7RosVfVfTUvwtAF3ZaV6uMRwYa5ukthpNXtmtpkOVh2aEKaKoqVBPPEN7zgXR3Dsq3hNq%2FxuKWT%2Bt%2Bg9zkG1utMa2BoNn%2FFS36sumbvIISeqq4dbQF6Pz%2BjhXD%2BLGEC733CGQxbNhHeFKUeRWRmnol%2FJe3kr5gva%2FV1HZkw%2BdOR2AY6mQFx%2BCSNAyF%2FUw6YipM0tdywkP7cTtVbmr%2Fjl7AYz7re5CrBW3DksZCEeeFxD1mcu1Kfiuwb5ekvtpItdTZFqrDdQgAY11DCDlxqH%2Fhg0xiTfG4mjgQ6rFwxs3gNUsWAXSty%2Bv1dSP18yjX361ciIizaicJV8csCz9BZoeCAQZxANYwyF4fZmaexial4E7v7dx54Zp0FAYtNwog%3D&X-Amz-SignedHeaders=host&x-id=GetObject&X-Amz-Signature=f996fc16b9cda276679d78a987a36ac01a779057a5ec4b0ee864ff857df76e3b)

## Właściwa korekta struktury

Należy zastąpić obecny fragment:

python

`if (pressed14, pressed15) != (previous14, previous15):     if time.monotonic() - buttons_changed_at >= 0.05:         if pressed14 and pressed15:             both_latched = True             screen = "menu"             menu_index = 0             menu_note = ""         elif both_latched:             if not pressed14 and not pressed15:                 both_latched = False         else:             released14 = previous14 and not pressed14            released15 = previous15 and not pressed15             if screen == "menu":`

na:

python

`if pressed14 and pressed15:     if time.monotonic() - buttons_changed_at >= 0.05:         both_latched = True         screen = "menu"         menu_index = 0         menu_note = "" elif both_latched:     if not pressed14 and not pressed15:         both_latched = False else:     released14 = previous14 and not pressed14    released15 = previous15 and not pressed15     if screen == "menu":`

Kluczowa różnica: blok `else:` z obsługą ekranów ma wykonywać się **w każdej iteracji pętli**, a nie tylko przy zmianie stanu przycisków.[code.py](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/157352839/fc83ea8e-a0f0-407e-9d65-337a5492159d/code.py?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Checksum-Mode=ENABLED&X-Amz-Credential=ASIA2F3EMEYEYIWZKYM7%2F20261123%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20261123T163439Z&X-Amz-Expires=3245&X-Amz-Security-Token=IQoJb3JpZ2luX2VjELH%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJGMEQCIB%2FZ46iOp8GIqXKE8gQH6dKQQNt776ppylhM0CCgugyxAiBrmhnDjc7NCA3hxCOQ7ws%2FhDBymKM%2B6Zza7p8NULdFeyqABQh6EAEaDDY5OTc1MzMwOTcwNSIMLi%2BJ6cClgDGaxDlCKt0EB4cEPEevk2CfDpzFwYi2%2FJPRMsLWQlirMa7J58H2Ff9TRsOcpMj1Fe8XEygXAPAmDbXuGKtGp7ebgeNUS%2FmKx%2BpwvFQgCRAZXB8YcniYma6yjx5EZ3lbE81dsz5p2RZX3FqjFhGcTpS13LUjF2jd1SbyJb5TDdtHVwnqbvvzUxQ56dAcQqq0gKKqJqwMv39iu8G%2FwxoWodqz%2FtHDVAfDX7FMjVlA55WpqDswlVF8jf1BSJ%2BaXE8ORQSeBuDAFXLdXebBjPR5JfvpSCiZ5kcpsgoZ1EIESvi7nI2tWItk2ZMpuAHLKJZWr06RL6I%2BN3uCDNG6R4WY%2FUJMYCysUeIazPFR9fqvCJWC9gojA%2BgNxYMGguHBsUkXyAIwGN2MMsve1yMxYgk3O8M%2FceB4oEuZd29bQEPoVTIGC0oEWqKorVlN7ha8m4kJSvBtG0m%2FKw1KD6HLKkz0901DzonVCVjIkz9d79JaGIP1U3hDSojyYrm4gbRtOJ0Bfi2JRUHyJq3CaiJNmxPNQQjIIIYn4C%2FXnfURISGWjDcMfZYAW5lb3VCnp9%2BmjC1UxVHcItpUZyfvuESKLMK3guK5DwAeJfeYcAvB1FW5ohIgcxELYmfhkOAeDOtihQ9eNH5V%2FP8tO5a3K7RosVfVfTUvwtAF3ZaV6uMRwYa5ukthpNXtmtpkOVh2aEKaKoqVBPPEN7zgXR3Dsq3hNq%2FxuKWT%2Bt%2Bg9zkG1utMa2BoNn%2FFS36sumbvIISeqq4dbQF6Pz%2BjhXD%2BLGEC733CGQxbNhHeFKUeRWRmnol%2FJe3kr5gva%2FV1HZkw%2BdOR2AY6mQFx%2BCSNAyF%2FUw6YipM0tdywkP7cTtVbmr%2Fjl7AYz7re5CrBW3DksZCEeeFxD1mcu1Kfiuwb5ekvtpItdTZFqrDdQgAY11DCDlxqH%2Fhg0xiTfG4mjgQ6rFwxs3gNUsWAXSty%2Bv1dSP18yjX361ciIizaicJV8csCz9BZoeCAQZxANYwyF4fZmaexial4E7v7dx54Zp0FAYtNwog%3D&X-Amz-SignedHeaders=host&x-id=GetObject&X-Amz-Signature=f996fc16b9cda276679d78a987a36ac01a779057a5ec4b0ee864ff857df76e3b)

## Problem z wcięciami

Podczas ręcznej edycji pojawił się błąd:

text

`IndentationError: unindent doesn't match any outer indent level`

w okolicach linii 754–755. Wynikał z niejednolitego wcięcia po zmianie warunku `if (pressed14, pressed15) != ...` oraz z pozostawienia wewnętrznego, zdublowanego `if pressed14 and pressed15:`.[code.py](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/157352839/fc83ea8e-a0f0-407e-9d65-337a5492159d/code.py?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Checksum-Mode=ENABLED&X-Amz-Credential=ASIA2F3EMEYEYIWZKYM7%2F20261123%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20261123T163439Z&X-Amz-Expires=3245&X-Amz-Security-Token=IQoJb3JpZ2luX2VjELH%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJGMEQCIB%2FZ46iOp8GIqXKE8gQH6dKQQNt776ppylhM0CCgugyxAiBrmhnDjc7NCA3hxCOQ7ws%2FhDBymKM%2B6Zza7p8NULdFeyqABQh6EAEaDDY5OTc1MzMwOTcwNSIMLi%2BJ6cClgDGaxDlCKt0EB4cEPEevk2CfDpzFwYi2%2FJPRMsLWQlirMa7J58H2Ff9TRsOcpMj1Fe8XEygXAPAmDbXuGKtGp7ebgeNUS%2FmKx%2BpwvFQgCRAZXB8YcniYma6yjx5EZ3lbE81dsz5p2RZX3FqjFhGcTpS13LUjF2jd1SbyJb5TDdtHVwnqbvvzUxQ56dAcQqq0gKKqJqwMv39iu8G%2FwxoWodqz%2FtHDVAfDX7FMjVlA55WpqDswlVF8jf1BSJ%2BaXE8ORQSeBuDAFXLdXebBjPR5JfvpSCiZ5kcpsgoZ1EIESvi7nI2tWItk2ZMpuAHLKJZWr06RL6I%2BN3uCDNG6R4WY%2FUJMYCysUeIazPFR9fqvCJWC9gojA%2BgNxYMGguHBsUkXyAIwGN2MMsve1yMxYgk3O8M%2FceB4oEuZd29bQEPoVTIGC0oEWqKorVlN7ha8m4kJSvBtG0m%2FKw1KD6HLKkz0901DzonVCVjIkz9d79JaGIP1U3hDSojyYrm4gbRtOJ0Bfi2JRUHyJq3CaiJNmxPNQQjIIIYn4C%2FXnfURISGWjDcMfZYAW5lb3VCnp9%2BmjC1UxVHcItpUZyfvuESKLMK3guK5DwAeJfeYcAvB1FW5ohIgcxELYmfhkOAeDOtihQ9eNH5V%2FP8tO5a3K7RosVfVfTUvwtAF3ZaV6uMRwYa5ukthpNXtmtpkOVh2aEKaKoqVBPPEN7zgXR3Dsq3hNq%2FxuKWT%2Bt%2Bg9zkG1utMa2BoNn%2FFS36sumbvIISeqq4dbQF6Pz%2BjhXD%2BLGEC733CGQxbNhHeFKUeRWRmnol%2FJe3kr5gva%2FV1HZkw%2BdOR2AY6mQFx%2BCSNAyF%2FUw6YipM0tdywkP7cTtVbmr%2Fjl7AYz7re5CrBW3DksZCEeeFxD1mcu1Kfiuwb5ekvtpItdTZFqrDdQgAY11DCDlxqH%2Fhg0xiTfG4mjgQ6rFwxs3gNUsWAXSty%2Bv1dSP18yjX361ciIizaicJV8csCz9BZoeCAQZxANYwyF4fZmaexial4E7v7dx54Zp0FAYtNwog%3D&X-Amz-SignedHeaders=host&x-id=GetObject&X-Amz-Signature=f996fc16b9cda276679d78a987a36ac01a779057a5ec4b0ee864ff857df76e3b)

W celu uniknięcia dalszych błędów przygotowano kompletny, poprawiony blok głównej pętli `while running:` — od `while running:` aż do `time.sleep(0.02)`. Ma on zostać wklejony jako całość w miejsce obecnej pętli.[code.py](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/157352839/fc83ea8e-a0f0-407e-9d65-337a5492159d/code.py?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Checksum-Mode=ENABLED&X-Amz-Credential=ASIA2F3EMEYEYIWZKYM7%2F20261123%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20261123T163439Z&X-Amz-Expires=3245&X-Amz-Security-Token=IQoJb3JpZ2luX2VjELH%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJGMEQCIB%2FZ46iOp8GIqXKE8gQH6dKQQNt776ppylhM0CCgugyxAiBrmhnDjc7NCA3hxCOQ7ws%2FhDBymKM%2B6Zza7p8NULdFeyqABQh6EAEaDDY5OTc1MzMwOTcwNSIMLi%2BJ6cClgDGaxDlCKt0EB4cEPEevk2CfDpzFwYi2%2FJPRMsLWQlirMa7J58H2Ff9TRsOcpMj1Fe8XEygXAPAmDbXuGKtGp7ebgeNUS%2FmKx%2BpwvFQgCRAZXB8YcniYma6yjx5EZ3lbE81dsz5p2RZX3FqjFhGcTpS13LUjF2jd1SbyJb5TDdtHVwnqbvvzUxQ56dAcQqq0gKKqJqwMv39iu8G%2FwxoWodqz%2FtHDVAfDX7FMjVlA55WpqDswlVF8jf1BSJ%2BaXE8ORQSeBuDAFXLdXebBjPR5JfvpSCiZ5kcpsgoZ1EIESvi7nI2tWItk2ZMpuAHLKJZWr06RL6I%2BN3uCDNG6R4WY%2FUJMYCysUeIazPFR9fqvCJWC9gojA%2BgNxYMGguHBsUkXyAIwGN2MMsve1yMxYgk3O8M%2FceB4oEuZd29bQEPoVTIGC0oEWqKorVlN7ha8m4kJSvBtG0m%2FKw1KD6HLKkz0901DzonVCVjIkz9d79JaGIP1U3hDSojyYrm4gbRtOJ0Bfi2JRUHyJq3CaiJNmxPNQQjIIIYn4C%2FXnfURISGWjDcMfZYAW5lb3VCnp9%2BmjC1UxVHcItpUZyfvuESKLMK3guK5DwAeJfeYcAvB1FW5ohIgcxELYmfhkOAeDOtihQ9eNH5V%2FP8tO5a3K7RosVfVfTUvwtAF3ZaV6uMRwYa5ukthpNXtmtpkOVh2aEKaKoqVBPPEN7zgXR3Dsq3hNq%2FxuKWT%2Bt%2Bg9zkG1utMa2BoNn%2FFS36sumbvIISeqq4dbQF6Pz%2BjhXD%2BLGEC733CGQxbNhHeFKUeRWRmnol%2FJe3kr5gva%2FV1HZkw%2BdOR2AY6mQFx%2BCSNAyF%2FUw6YipM0tdywkP7cTtVbmr%2Fjl7AYz7re5CrBW3DksZCEeeFxD1mcu1Kfiuwb5ekvtpItdTZFqrDdQgAY11DCDlxqH%2Fhg0xiTfG4mjgQ6rFwxs3gNUsWAXSty%2Bv1dSP18yjX361ciIizaicJV8csCz9BZoeCAQZxANYwyF4fZmaexial4E7v7dx54Zp0FAYtNwog%3D&X-Amz-SignedHeaders=host&x-id=GetObject&X-Amz-Signature=f996fc16b9cda276679d78a987a36ac01a779057a5ec4b0ee864ff857df76e3b)

## Aktualny stan kodu

Aktualny `code.py` zawiera:

- funkcję `auto_repeat()`,

- zmienne `last14`, `delay14`, `last15`, `delay15`,

- obliczanie `step14` i `step15` na początku pętli,

- print diagnostyczny `BTN14=...`,

- automatyczne zwiększanie `edit_hour` i `edit_minute` przez `step14`,

- automatyczne przewijanie `script_index`, `schedule_index` i `plan_action_index` przez `step15`,

- printy diagnostyczne, które można później usunąć.[code.py](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/157352839/fc83ea8e-a0f0-407e-9d65-337a5492159d/code.py?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Checksum-Mode=ENABLED&X-Amz-Credential=ASIA2F3EMEYEYIWZKYM7%2F20261123%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20261123T163439Z&X-Amz-Expires=3245&X-Amz-Security-Token=IQoJb3JpZ2luX2VjELH%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJGMEQCIB%2FZ46iOp8GIqXKE8gQH6dKQQNt776ppylhM0CCgugyxAiBrmhnDjc7NCA3hxCOQ7ws%2FhDBymKM%2B6Zza7p8NULdFeyqABQh6EAEaDDY5OTc1MzMwOTcwNSIMLi%2BJ6cClgDGaxDlCKt0EB4cEPEevk2CfDpzFwYi2%2FJPRMsLWQlirMa7J58H2Ff9TRsOcpMj1Fe8XEygXAPAmDbXuGKtGp7ebgeNUS%2FmKx%2BpwvFQgCRAZXB8YcniYma6yjx5EZ3lbE81dsz5p2RZX3FqjFhGcTpS13LUjF2jd1SbyJb5TDdtHVwnqbvvzUxQ56dAcQqq0gKKqJqwMv39iu8G%2FwxoWodqz%2FtHDVAfDX7FMjVlA55WpqDswlVF8jf1BSJ%2BaXE8ORQSeBuDAFXLdXebBjPR5JfvpSCiZ5kcpsgoZ1EIESvi7nI2tWItk2ZMpuAHLKJZWr06RL6I%2BN3uCDNG6R4WY%2FUJMYCysUeIazPFR9fqvCJWC9gojA%2BgNxYMGguHBsUkXyAIwGN2MMsve1yMxYgk3O8M%2FceB4oEuZd29bQEPoVTIGC0oEWqKorVlN7ha8m4kJSvBtG0m%2FKw1KD6HLKkz0901DzonVCVjIkz9d79JaGIP1U3hDSojyYrm4gbRtOJ0Bfi2JRUHyJq3CaiJNmxPNQQjIIIYn4C%2FXnfURISGWjDcMfZYAW5lb3VCnp9%2BmjC1UxVHcItpUZyfvuESKLMK3guK5DwAeJfeYcAvB1FW5ohIgcxELYmfhkOAeDOtihQ9eNH5V%2FP8tO5a3K7RosVfVfTUvwtAF3ZaV6uMRwYa5ukthpNXtmtpkOVh2aEKaKoqVBPPEN7zgXR3Dsq3hNq%2FxuKWT%2Bt%2Bg9zkG1utMa2BoNn%2FFS36sumbvIISeqq4dbQF6Pz%2BjhXD%2BLGEC733CGQxbNhHeFKUeRWRmnol%2FJe3kr5gva%2FV1HZkw%2BdOR2AY6mQFx%2BCSNAyF%2FUw6YipM0tdywkP7cTtVbmr%2Fjl7AYz7re5CrBW3DksZCEeeFxD1mcu1Kfiuwb5ekvtpItdTZFqrDdQgAY11DCDlxqH%2Fhg0xiTfG4mjgQ6rFwxs3gNUsWAXSty%2Bv1dSP18yjX361ciIizaicJV8csCz9BZoeCAQZxANYwyF4fZmaexial4E7v7dx54Zp0FAYtNwog%3D&X-Amz-SignedHeaders=host&x-id=GetObject&X-Amz-Signature=f996fc16b9cda276679d78a987a36ac01a779057a5ec4b0ee864ff857df76e3b)

Jednak **struktura obsługi przycisków nadal zawiera stary warunek zmiany stanu**, przez który auto-repeat nie dochodzi do sekcji inkrementacji. Dlatego obecnie przytrzymanie `GP14` generuje `STEP14=True`, ale nie zwiększa godziny ani minuty.[code.py](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/157352839/fc83ea8e-a0f0-407e-9d65-337a5492159d/code.py?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Checksum-Mode=ENABLED&X-Amz-Credential=ASIA2F3EMEYEYIWZKYM7%2F20261123%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20261123T163439Z&X-Amz-Expires=3245&X-Amz-Security-Token=IQoJb3JpZ2luX2VjELH%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJGMEQCIB%2FZ46iOp8GIqXKE8gQH6dKQQNt776ppylhM0CCgugyxAiBrmhnDjc7NCA3hxCOQ7ws%2FhDBymKM%2B6Zza7p8NULdFeyqABQh6EAEaDDY5OTc1MzMwOTcwNSIMLi%2BJ6cClgDGaxDlCKt0EB4cEPEevk2CfDpzFwYi2%2FJPRMsLWQlirMa7J58H2Ff9TRsOcpMj1Fe8XEygXAPAmDbXuGKtGp7ebgeNUS%2FmKx%2BpwvFQgCRAZXB8YcniYma6yjx5EZ3lbE81dsz5p2RZX3FqjFhGcTpS13LUjF2jd1SbyJb5TDdtHVwnqbvvzUxQ56dAcQqq0gKKqJqwMv39iu8G%2FwxoWodqz%2FtHDVAfDX7FMjVlA55WpqDswlVF8jf1BSJ%2BaXE8ORQSeBuDAFXLdXebBjPR5JfvpSCiZ5kcpsgoZ1EIESvi7nI2tWItk2ZMpuAHLKJZWr06RL6I%2BN3uCDNG6R4WY%2FUJMYCysUeIazPFR9fqvCJWC9gojA%2BgNxYMGguHBsUkXyAIwGN2MMsve1yMxYgk3O8M%2FceB4oEuZd29bQEPoVTIGC0oEWqKorVlN7ha8m4kJSvBtG0m%2FKw1KD6HLKkz0901DzonVCVjIkz9d79JaGIP1U3hDSojyYrm4gbRtOJ0Bfi2JRUHyJq3CaiJNmxPNQQjIIIYn4C%2FXnfURISGWjDcMfZYAW5lb3VCnp9%2BmjC1UxVHcItpUZyfvuESKLMK3guK5DwAeJfeYcAvB1FW5ohIgcxELYmfhkOAeDOtihQ9eNH5V%2FP8tO5a3K7RosVfVfTUvwtAF3ZaV6uMRwYa5ukthpNXtmtpkOVh2aEKaKoqVBPPEN7zgXR3Dsq3hNq%2FxuKWT%2Bt%2Bg9zkG1utMa2BoNn%2FFS36sumbvIISeqq4dbQF6Pz%2BjhXD%2BLGEC733CGQxbNhHeFKUeRWRmnol%2FJe3kr5gva%2FV1HZkw%2BdOR2AY6mQFx%2BCSNAyF%2FUw6YipM0tdywkP7cTtVbmr%2Fjl7AYz7re5CrBW3DksZCEeeFxD1mcu1Kfiuwb5ekvtpItdTZFqrDdQgAY11DCDlxqH%2Fhg0xiTfG4mjgQ6rFwxs3gNUsWAXSty%2Bv1dSP18yjX361ciIizaicJV8csCz9BZoeCAQZxANYwyF4fZmaexial4E7v7dx54Zp0FAYtNwog%3D&X-Amz-SignedHeaders=host&x-id=GetObject&X-Amz-Signature=f996fc16b9cda276679d78a987a36ac01a779057a5ec4b0ee864ff857df76e3b)

## Co zrobić w kolejnym kroku

1. Otworzyć `code.py`.

2. Znaleźć początek głównej pętli: `while running:`.

3. Usunąć całą obecną pętlę aż do końca pliku.

4. Wkleić kompletny, poprawiony blok pętli przygotowany w tej sesji.

5. Uruchomić kod w Thonny.

6. Wejść w `HARMONOGRAM`, wybrać wpis i przejść do `USTAW CZAS`.

7. Przytrzymać `GP14` — godzina powinna rosnąć, a potem po przejściu do minut również minuty.

8. Wejść w `URUCHOM MAKRO` i przytrzymać `GP15` — lista makr powinna przewijać się automatycznie.

9. Po potwierdzeniu działania usunąć print diagnostyczny `BTN14=...`.

10. Zostawić printy błędów w blokach `except`.[code.py](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/157352839/fc83ea8e-a0f0-407e-9d65-337a5492159d/code.py?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Checksum-Mode=ENABLED&X-Amz-Credential=ASIA2F3EMEYEYIWZKYM7%2F20261123%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20261123T163439Z&X-Amz-Expires=3245&X-Amz-Security-Token=IQoJb3JpZ2luX2VjELH%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJGMEQCIB%2FZ46iOp8GIqXKE8gQH6dKQQNt776ppylhM0CCgugyxAiBrmhnDjc7NCA3hxCOQ7ws%2FhDBymKM%2B6Zza7p8NULdFeyqABQh6EAEaDDY5OTc1MzMwOTcwNSIMLi%2BJ6cClgDGaxDlCKt0EB4cEPEevk2CfDpzFwYi2%2FJPRMsLWQlirMa7J58H2Ff9TRsOcpMj1Fe8XEygXAPAmDbXuGKtGp7ebgeNUS%2FmKx%2BpwvFQgCRAZXB8YcniYma6yjx5EZ3lbE81dsz5p2RZX3FqjFhGcTpS13LUjF2jd1SbyJb5TDdtHVwnqbvvzUxQ56dAcQqq0gKKqJqwMv39iu8G%2FwxoWodqz%2FtHDVAfDX7FMjVlA55WpqDswlVF8jf1BSJ%2BaXE8ORQSeBuDAFXLdXebBjPR5JfvpSCiZ5kcpsgoZ1EIESvi7nI2tWItk2ZMpuAHLKJZWr06RL6I%2BN3uCDNG6R4WY%2FUJMYCysUeIazPFR9fqvCJWC9gojA%2BgNxYMGguHBsUkXyAIwGN2MMsve1yMxYgk3O8M%2FceB4oEuZd29bQEPoVTIGC0oEWqKorVlN7ha8m4kJSvBtG0m%2FKw1KD6HLKkz0901DzonVCVjIkz9d79JaGIP1U3hDSojyYrm4gbRtOJ0Bfi2JRUHyJq3CaiJNmxPNQQjIIIYn4C%2FXnfURISGWjDcMfZYAW5lb3VCnp9%2BmjC1UxVHcItpUZyfvuESKLMK3guK5DwAeJfeYcAvB1FW5ohIgcxELYmfhkOAeDOtihQ9eNH5V%2FP8tO5a3K7RosVfVfTUvwtAF3ZaV6uMRwYa5ukthpNXtmtpkOVh2aEKaKoqVBPPEN7zgXR3Dsq3hNq%2FxuKWT%2Bt%2Bg9zkG1utMa2BoNn%2FFS36sumbvIISeqq4dbQF6Pz%2BjhXD%2BLGEC733CGQxbNhHeFKUeRWRmnol%2FJe3kr5gva%2FV1HZkw%2BdOR2AY6mQFx%2BCSNAyF%2FUw6YipM0tdywkP7cTtVbmr%2Fjl7AYz7re5CrBW3DksZCEeeFxD1mcu1Kfiuwb5ekvtpItdTZFqrDdQgAY11DCDlxqH%2Fhg0xiTfG4mjgQ6rFwxs3gNUsWAXSty%2Bv1dSP18yjX361ciIizaicJV8csCz9BZoeCAQZxANYwyF4fZmaexial4E7v7dx54Zp0FAYtNwog%3D&X-Amz-SignedHeaders=host&x-id=GetObject&X-Amz-Signature=f996fc16b9cda276679d78a987a36ac01a779057a5ec4b0ee864ff857df76e3b)

## Ważne reguły na przyszłość

- Przy korektach zawsze podawać **dwie unikalne linie kotwicy**, aby jednoznacznie wskazać miejsce w kodzie.

- Nie dodawać drugiego wywołania `auto_repeat()` w środku obsługi przycisków — powoduje to podwójne liczenie czasu i psuje powtarzanie.

- Nie umieszczać obsługi `step14` / `step15` wewnątrz warunku wykrywania zmiany stanu przycisków.

- `released14` i `released15` zostawić wyłącznie dla akcji jednorazowych: zatwierdzenia, wejścia dalej, cofania, zapisu.

- `step14` i `step15` używać wyłącznie do powtarzalnych akcji: zwiększania wartości i przewijania list.

- OLED odświeżać bezpośrednio po zmianie wartości oraz ustawiać `last_refresh = time.monotonic()`.
