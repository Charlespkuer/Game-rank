import name0
import random
import curses
import pickle
import os

def save_data(indicators, visited_combinations):
    with open('game_data.pkl', 'wb') as f:
        pickle.dump((indicators, visited_combinations), f)

def load_data():
    if os.path.exists('game_data.pkl'):
        with open('game_data.pkl', 'rb') as f:
            return pickle.load(f)
    else:
        return None

def main(stdscr):
    # 初始化 curses
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)
    choices_history = []

    # 尝试读取保存的数据
    loaded_data = load_data()
    if loaded_data:
        indicators, visited_combinations = loaded_data
    else:
        # 初始化指标字典
        indicators = {name: 0 for name in name0.list}
        # 记录已经遍历过的组合
        visited_combinations = set()

    names_len = len(name0.list)# 随机选择组合进行比较
    current_judgement_count = 0  # 初始化当前判断次数
    total_judgements_needed = names_len * (names_len - 1) / 2  # 计算所需的总判断次数

    while len(visited_combinations) < total_judgements_needed:
        # 动态生成并选择一个未遍历的组合
        while True:
            combo = tuple(random.sample(list(name0.list), 2))
            if combo not in visited_combinations and (combo[1], combo[0]) not in visited_combinations:
                visited_combinations.add(combo)
                break

        while True:
            stdscr.clear()
            stdscr.addstr(0, 0, f"请选择以下两个元素中的一个：1. {combo[0]} 或 2. {combo[1]}")
            stdscr.addstr(1, 0, "按下 1 选择左边，按下 2 选择右边，按下 q 退出")
            # 显示当前判断次数/总判断次数
            stdscr.addstr(2, 0, f"当前判断次数/总判断次数: {current_judgement_count}/{int(total_judgements_needed)}")
            stdscr.refresh()

            key = stdscr.getch()
            if key == ord('1') or key == ord('2'):
                selected = combo[0] if key == ord('1') else combo[1]
                # 更新 indicators
                indicators[selected] += 1
                # 记录这次选择
                choices_history.append((combo, selected))
                current_judgement_count += 1
                break
            elif key == curses.KEY_BACKSPACE:
                if choices_history:
                    last_choice, last_selected = choices_history.pop()
                    # 撤销上一次的选择
                    visited_combinations.remove(last_choice)
                    indicators[last_selected] -= 1
                    # 不退出循环，让用户重新选择
                    current_judgement_count -= 1
                    continue
            elif key == ord('q'):
                # 保存数据并退出的代码保持不变
                save_data(indicators, visited_combinations)
                return

    # 按指标排序并显示结果
    sorted_indicators = sorted(indicators.items(), key=lambda x: x[1], reverse=True)

    page = 0  # 初始化当前页码
    while True:
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()
        items_per_page = max_y - 3  # 留出空间显示操作提示
        pages = len(sorted_indicators) // items_per_page + (1 if len(sorted_indicators) % items_per_page > 0 else 0)

        stdscr.addstr(0, 0, "游戏喜爱指数：")
        start_index = page * items_per_page
        end_index = start_index + items_per_page
        for i, (name, indicator) in enumerate(sorted_indicators[start_index:end_index], start=1):
            stdscr.addstr(i, 0, f"{name}: {indicator}")
        stdscr.addstr(max_y - 2, 0, f"页码：{page + 1}/{pages} - ad箭头翻页，按下 q 退出")
        stdscr.refresh()

        key = stdscr.getch()
        if key == ord('q'):
            break
        elif key == ord('a') and page > 0:
            page -= 1  # 上一页
        elif key == ord('d') and page < pages - 1:
            page += 1  # 下一页

curses.wrapper(main)